// Replace every CONFIGURE_* value with the exact wording from the approved
// ethics application and Prolific study before recruitment. The site remains
// locked until ethics.status is "APPROVED" and all required values are set.
export const studyConfig = {
  ethics: {
    status: "PENDING_CONFIGURATION",
    institution: "CONFIGURE_INSTITUTION",
    reference: "CONFIGURE_APPROVAL_REFERENCE",
    approvedDate: "CONFIGURE_APPROVAL_DATE",
    contactName: "CONFIGURE_RESEARCHER_NAME",
    contactEmail: "CONFIGURE_RESEARCHER_EMAIL"
  },
  study: {
    estimatedMinutes: "CONFIGURE_ESTIMATED_MINUTES",
    payment: "CONFIGURE_PAYMENT_AND_RATE",
    risks: "Minimal risk: possible fatigue or mild frustration from text-classification tasks.",
    withdrawal: "Participants may leave before final submission. After submission, withdrawal is possible only while the hashed Prolific identifier can still be linked by the research team."
  },
  prolific: {
    completionCode: "CONFIGURE_COMPLETION_CODE",
    completionUrl: "https://app.prolific.com/submissions/complete?cc=CONFIGURE_COMPLETION_CODE",
    expectedStudyId: ""
  }
};
