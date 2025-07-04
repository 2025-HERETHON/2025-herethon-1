import { Header2 } from "./components/Header2.js";
import { Footer } from "./components/Footer.js";
import { renderVoteBlock } from "./components/VoteBlock.js";
document.getElementById("header").innerHTML = `
${Header2()}
`;
document.getElementById("footer").innerHTML = `
${Footer()}
`;

document.querySelectorAll(".ai-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    btn.classList.toggle("active");
  });
});

document
  .querySelectorAll(
    ".community-vote-button1, .community-vote-button2, .community-vote-button3"
  )
  .forEach((btn) => {
    btn.addEventListener("click", () => {
      // 이미 active 상태라면 해제
      const isActive = btn.classList.contains("active");

      // 모든 버튼에서 active 제거
      document
        .querySelectorAll(
          ".community-vote-button1, .community-vote-button2, .community-vote-button3"
        )
        .forEach((el) => {
          el.classList.remove("active");
        });

      // 이전에 active였던 버튼이 아니면 새로 추가
      if (!isActive) {
        btn.classList.add("active");
      }
      // 같으면 아무것도 안 해도 됨 (active 제거된 상태 유지)
    });
  });

document.querySelectorAll(".delete-button1").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".inputplace").forEach((input) => {
      input.value = "";
    });
  });
});

document.addEventListener("DOMContentLoaded", () => {
  renderVoteBlock();
});
