export function VoteItem({ label, text, percent }) {
  return `
    <div class="community-vote">
      <div class="a">${label}</div>
      <div class="div5">${text}</div>
      <div class="percent1">${percent}</div>
    </div>
  `;
}
