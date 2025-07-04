import { VoteItem } from "./VoteItem.js";
import { Comment } from "./Comment.js";

// 다중 블록을 렌더링할 수 있게 수정
export function renderVoteBlock() {
  const voteData = [
    {
      voteId: "vote-item-block1",
      label: "A",
      text: "정당한 보상이다.",
      percent: "40%",
      comments: [
        { id: "comment1", opinion: "agree" },
        { id: "comment2", opinion: "agree" },
        { id: "comment3", opinion: "agree" },
      ],
    },
    {
      voteId: "vote-item-block2",
      label: "B",
      text: "과도한 보상이다.",
      percent: "30%",
      comments: [
        { id: "comment4", opinion: "oppose" },
        { id: "comment5", opinion: "oppose" },
        { id: "comment6", opinion: "oppose" },
      ],
    },
    {
      voteId: "vote-item-block3",
      label: "C",
      text: "보상이 필요 없다.",
      percent: "30%",
      comments: [
        { id: "comment7", opinion: "neutral" },
        { id: "comment8", opinion: "neutral" },
        { id: "comment9", opinion: "neutral" },
      ],
    },
  ];

  voteData.forEach((block) => {
    // 투표 항목 렌더링
    const voteContainer = document.getElementById(block.voteId);
    if (voteContainer) {
      voteContainer.innerHTML = VoteItem({
        label: block.label,
        text: block.text,
        percent: block.percent,
      });
    }

    // 댓글 렌더링
    block.comments.forEach((comment) => {
      const commentContainer = document.getElementById(comment.id);
      if (commentContainer) {
        commentContainer.innerHTML = Comment({
          nickname: "익명1",
          gender: "여성",
          date: "2025.07.02.",
          content: "내용이 나타나는 영역입니다. 레귤러사이즈입니다...",
          likes: 999,
          replies: 999,
          opinion: comment.opinion,
        });
      }
    });
  });
}
