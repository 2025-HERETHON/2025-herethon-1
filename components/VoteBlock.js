import { VoteItem } from "./VoteItem.js";
import { Comment } from "./Comment.js";

export function renderVoteBlock() {
  // 1. 전체 댓글 데이터 (서버에서 가져왔다고 가정)
  const allComments = [
    { id: "comment1", opinion: "agree" },
    { id: "comment2", opinion: "agree" },
    { id: "comment3", opinion: "agree" },
    { id: "comment4", opinion: "oppose" },
    { id: "comment5", opinion: "oppose" },
    { id: "comment6", opinion: "oppose" },
    { id: "comment7", opinion: "neutral" },
    { id: "comment8", opinion: "neutral" },
    { id: "comment9", opinion: "neutral" },
  ];

  // 2. opinion 기준으로 분류
  const agreeComments = allComments.filter((c) => c.opinion === "agree");
  const opposeComments = allComments.filter((c) => c.opinion === "oppose");
  const neutralComments = allComments.filter((c) => c.opinion === "neutral");

  // 3. 투표 데이터에 각 의견별 댓글 연결
  const voteData = [
    {
      voteId: "vote-item-block1",
      label: "A",
      text: "정당한 보상이다.",
      percent: "40%",
      comments: agreeComments,
    },
    {
      voteId: "vote-item-block2",
      label: "B",
      text: "과도한 보상이다.",
      percent: "30%",
      comments: opposeComments,
    },
    {
      voteId: "vote-item-block3",
      label: "C",
      text: "보상이 필요 없다.",
      percent: "30%",
      comments: neutralComments,
    },
  ];

  // 4. 블록 & 댓글 렌더링
  voteData.forEach((block) => {
    const voteContainer = document.getElementById(block.voteId);
    if (voteContainer) {
      voteContainer.innerHTML = VoteItem({
        label: block.label,
        text: block.text,
        percent: block.percent,
      });
    }

    block.comments.forEach((comment) => {
      const commentContainer = document.getElementById(comment.id);
      if (commentContainer) {
        commentContainer.innerHTML = Comment({
          nickname: "익명1",
          gender: "여성",
          date: "2025.07.02.",
          content:
            "내용이 나타나는 영역입니다. 레귤러사이즈입니다.내용이 나타나는 영역입니다. 레귤러사이즈입니다.내용이 나타나는 영역입니다. 레귤러사이즈입니다.",
          likes: 999,
          replies: 999,
          opinion: comment.opinion,
        });
      }
    });
  });
}
