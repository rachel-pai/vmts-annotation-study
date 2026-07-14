import{firebaseConfig}from"./firebase-config.js";

const $=s=>document.querySelector(s),screens=["intro","instructions","annotate","complete"];
const labels={
 revision_relation_label:[["replace","Replace","Earlier instruction is fully superseded"],["narrow","Narrow","Current instruction reduces the allowed scope"],["expand","Expand","Current instruction adds allowed scope"],["exception","Exception","Current instruction adds a special-case override"],["cancel","Cancel","Earlier instruction is withdrawn"],["reschedule","Reschedule","Timing changes while the task remains"],["clarify","Clarify","Meaning is clearer without a substantive change"],["unclear","Unclear","The relation cannot be determined"]],
 action_consistency_label:[["current","Current","Follows the current instruction"],["legacy","Legacy","Follows the earlier instruction instead"],["mixed","Mixed","Combines current and legacy requirements"],["abstention","Abstention","Explicitly defers, verifies, or does not act"],["unclear","Unclear","Cannot determine from the text"]],
 write_consistency_label:[["current","Current","Future agent inherits the current rule"],["legacy","Legacy","Future agent inherits the earlier rule"],["mixed","Mixed","Combines current and legacy rules"],["empty","Empty","No persistent instruction is saved"],["unclear","Unclear","Cannot determine what is inherited"]],
 mixed_validity_preservation_label:[["preserved","Preserved","Still-valid clause is retained correctly"],["corrupted_or_omitted","Corrupted / omitted","Still-valid clause is changed or missing"],["not_applicable","Not applicable","No still-valid clause is relevant"],["unclear","Unclear","Preservation cannot be determined"]]
};
const state={annotator:null,items:[],tasks:new Map(),index:0,answers:{},uid:null,db:null,online:false};

function show(id){screens.forEach(x=>$("#"+x).classList.toggle("active",x===id));scrollTo({top:0,behavior:"smooth"})}
function storageKey(){return`vmts_annotations_${state.annotator}`}
function optionHTML(name,values){return values.map(([v,l,h])=>`<label class="option"><input type="radio" name="${name}" value="${v}"><span><b>${l}</b>${h?`<small>${h}</small>`:""}</span></label>`).join("")}
function initOptions(){
 $("#revisionOptions").innerHTML=optionHTML("revision_relation_label",labels.revision_relation_label);
 $("#actionOptions").innerHTML=optionHTML("action_consistency_label",labels.action_consistency_label);
 $("#writeOptions").innerHTML=optionHTML("write_consistency_label",labels.write_consistency_label);
 $("#preservationOptions").innerHTML=optionHTML("mixed_validity_preservation_label",labels.mixed_validity_preservation_label);
 $("#confidenceOptions").innerHTML=optionHTML("confidence_1_to_5",[["1","1"],["2","2"],["3","3"],["4","4"],["5","5"]]);
}
async function loadData(){const[t,a]=await Promise.all([fetch("data/tasks.json").then(r=>r.json()),fetch("data/assignments.json").then(r=>r.json())]);state.tasks=new Map(t.map(x=>[x.item_id,x]));return a}
async function connectFirebase(){
 if(!firebaseConfig.apiKey)return $("#saveState").textContent="Local backup mode";
 try{
  const[{initializeApp},{getAuth,signInAnonymously},{getFirestore,doc,setDoc,serverTimestamp}]=await Promise.all([
   import("https://www.gstatic.com/firebasejs/12.16.0/firebase-app.js"),import("https://www.gstatic.com/firebasejs/12.16.0/firebase-auth.js"),import("https://www.gstatic.com/firebasejs/12.16.0/firebase-firestore.js")]);
  const app=initializeApp(firebaseConfig),auth=getAuth(app),cred=await signInAnonymously(auth);state.uid=cred.user.uid;state.db=getFirestore(app);state.firebase={doc,setDoc,serverTimestamp};
  await setDoc(doc(state.db,"claims",state.annotator),{uid:state.uid,annotatorId:state.annotator,claimedAt:serverTimestamp()});
  state.online=true;$("#saveState").textContent="Firebase connected";
 }catch(e){console.error(e);$("#saveState").textContent="Offline—saved locally"}
}
function restore(){try{state.answers=JSON.parse(localStorage.getItem(storageKey())||"{}")}catch{state.answers={}};const first=state.items.findIndex(id=>!state.answers[id]?.submitted);state.index=first<0?state.items.length:first}
function render(){
 if(state.index>=state.items.length)return finish();const id=state.items[state.index],t=state.tasks.get(id),a=state.answers[id]||{};
 $("#counter").textContent=`Item ${state.index+1} of ${state.items.length}`;$("#sessionHint").textContent=state.index===18?"Suggested break point":"";$("#progressBar").style.width=`${100*state.index/state.items.length}%`;
 const fieldMap=[["oldAction","old_action","Earlier instruction"],["currentAction","current_action","Current instruction"],["preserved","preserved_clause","Still-valid clause"],["invalidated","invalidated_clause","Invalidated clause"],["newClause","new_clause","New clause"],["candidateAction","candidate_action","Candidate action"],["candidateWrite","candidate_write","Candidate saved write"]],truncated=new Set(t.truncated_fields||[]);
 fieldMap.forEach(([el,k])=>{const node=$("#"+el);node.textContent=t[k]||"(empty)";node.classList.toggle("is-truncated",truncated.has(k))});
 const names=fieldMap.filter(([,k])=>truncated.has(k)).map(([, ,name])=>name),warning=$("#truncationWarning");warning.hidden=!names.length;warning.textContent=names.length?`Source-data warning: ${names.join(", ")} reached the generation limit and may be truncated. Treat the visible text as incomplete.`:"";
 $("#annotationForm").reset();Object.entries(a).forEach(([k,v])=>{const x=document.querySelector(`[name="${k}"][value="${CSS.escape(String(v))}"]`);if(x)x.checked=true});$("#notes").value=a.notes||"";$("#formError").textContent="";
}
function collect(){const fd=new FormData($("#annotationForm")),o={};for(const k of Object.keys(labels))o[k]=fd.get(k);o.confidence_1_to_5=fd.get("confidence_1_to_5");o.notes=$("#notes").value.trim();return o}
async function saveCurrent(){
 const itemId=state.items[state.index],answer=collect(),missing=[...Object.keys(labels),"confidence_1_to_5"].filter(k=>!answer[k]);if(missing.length){$("#formError").textContent="Please answer all five required questions.";return false}
 const payload={...answer,itemId,annotatorId:state.annotator,uid:state.uid||"local",submitted:true,clientUpdatedAt:new Date().toISOString()};state.answers[itemId]=payload;localStorage.setItem(storageKey(),JSON.stringify(state.answers));$("#saveState").textContent="Saved locally";
 if(state.online){try{const{doc,setDoc,serverTimestamp}=state.firebase;await setDoc(doc(state.db,"responses",`${state.annotator}_${itemId}`),{...payload,uid:state.uid,serverUpdatedAt:serverTimestamp()},{merge:true});$("#saveState").textContent="Saved to Firebase"}catch(e){console.error(e);$("#saveState").textContent="Firebase failed—local copy safe"}}
 return true
}
function finish(){show("complete");const code=`VMTS-${state.annotator}-${Object.keys(state.answers).length}-${state.uid?.slice(0,8)||"LOCAL"}`;$("#completionCode").textContent=code}
function download(){const blob=new Blob([JSON.stringify({annotatorId:state.annotator,responses:Object.values(state.answers)},null,2)],{type:"application/json"}),a=document.createElement("a");a.href=URL.createObjectURL(blob);a.download=`vmts-${state.annotator}-backup.json`;a.click();URL.revokeObjectURL(a.href)}

initOptions();
$("#beginBtn").onclick=async()=>{const annotator=(new URLSearchParams(location.search).get("annotator")||"").toUpperCase();if(!$("#consentCheck").checked)return $("#introError").textContent="Consent is required to participate.";if(!["A","B","C","D","E","F"].includes(annotator))return $("#introError").textContent="This study link is incomplete. Please use the personal link sent by the researcher.";state.annotator=annotator;const assignments=await loadData();state.items=assignments[annotator];restore();await connectFirebase();if(firebaseConfig.apiKey&&!state.online)return $("#introError").textContent="This annotation slot is already claimed or anonymous sign-in is not enabled. Contact the researcher.";show("instructions")};
$("#startBtn").onclick=()=>{if(state.index>=36)return finish();show("annotate");render()};
$("#annotationForm").onsubmit=async e=>{e.preventDefault();if(await saveCurrent()){state.index++;render()}};
$("#backBtn").onclick=()=>{if(state.index>0){state.index--;render()}};$("#exportBtn").onclick=download;
$("#clearBtn").onclick=()=>{$("#annotationForm").reset();$("#notes").value="";$("#formError").textContent=""};
