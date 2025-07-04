import { Header2 } from "./components/Header2.js";
import { Footer } from "./components/Footer.js";
import { renderVoteBlock } from "./components/VoteBlock.js";
import { ArticleCard } from "./components/ArticleCard.js";

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

document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".more-see").forEach((button) => {
    button.addEventListener("click", () => {
      const textBox = button.closest(".text").querySelector(".comment-place");

      // 현재 확장 상태인지 확인
      const isExpanded = textBox.classList.contains("expanded");

      // 토글 로직
      if (isExpanded) {
        textBox.classList.remove("expanded");
        button.textContent = "더보기";
      } else {
        textBox.classList.add("expanded");
        button.textContent = "접기";
      }
    });
  });
});

document.getElementById("article-card-relation").innerHTML += ArticleCard({
  thumbnail:
    "https://search.pstatic.net/sunny/?src=http%3A%2F%2Ffile3.instiz.net%2Fdata%2Fcached_img%2Fupload%2F2024%2F07%2F23%2F18%2F38929c021771c5500274c098df0c06e2.jpg&type=sc960_832",
  title:
    "젠더 이슈와 관련된 논제를 적어 주세요.젠더 이슈를 적어 주세요.젠더 이슈를 적어 주세요.젠더 이슈를 적어 주세요.젠더 이슈를 적어 주세요.젠더 이슈를 적어 주세요.젠더 이슈를 적어 주세요.젠더 이슈를 적어 주세요.젠더 이슈",
  commentCount1: 999,
  commentCount2: 999,
});

const articleDataList = [
  {
    id: "article-card-recommend1",
    thumbnail:
      "https://search.pstatic.net/sunny/?src=http%3A%2F%2Ffile3.instiz.net%2Fdata%2Fcached_img%2Fupload%2F2024%2F07%2F23%2F18%2F38929c021771c5500274c098df0c06e2.jpg&type=sc960_832",
    title:
      "젠더 이슈와 관련된 논제를 적어 주세요.젠더 이슈를 적어 주세요...듀듀듀듀리쿠짱짱짱",
    commentCount1: 999,
    commentCount2: 999,
  },
  {
    id: "article-card-recommend2",
    thumbnail: "https://example.com/image2.jpg",
    title: "젠더 이슈 논제 예시 2입니다.",
    commentCount1: 111,
    commentCount2: 222,
  },
  {
    id: "article-card-recommend3",
    thumbnail: "https://example.com/image3.jpg",
    title: "젠더 관련 기사 제목 3입니다.",
    commentCount1: 333,
    commentCount2: 444,
  },
  {
    id: "article-card-recommend4",
    thumbnail: "https://example.com/image4.jpg",
    title: "젠더 주제 4번 제목입니다.",
    commentCount1: 555,
    commentCount2: 666,
  },
  {
    id: "article-card-recommend5",
    thumbnail: "https://example.com/image5.jpg",
    title: "젠더 논제 5번. 아주 긴 제목 테스트도 포함됩니다.",
    commentCount1: 777,
    commentCount2: 888,
  },
];

// 렌더링
articleDataList.forEach((item) => {
  const container = document.getElementById(item.id);
  if (container) {
    container.innerHTML = ArticleCard({
      thumbnail: item.thumbnail,
      title: item.title,
      commentCount1: item.commentCount1,
      commentCount2: item.commentCount2,
    });
  }
});
