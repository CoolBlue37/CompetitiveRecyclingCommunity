let counts = { 9: 0, 10: 0, 11: 0, 12: 0 };

function addPoint(grade) {
  counts[grade]++;

  let total = counts[9] + counts[10] + counts[11] + counts[12];
  document.getElementById("total").textContent = total;

  let highest = Math.max(counts[9], counts[10], counts[11], counts[12]);

  for (let g of [9, 10, 11, 12]) {
    let row = document.getElementById("grade-" + g);
    row.querySelector("span:last-child").textContent = counts[g];
    row.querySelector(":scope > div > div").style.width =
      (counts[g] / highest) * 100 + "%";
  }

  document.getElementById("message").textContent =
    "Thanks, " + grade + "th grade!";

  sortBoard();
}

function sortBoard() {
  let board = document.getElementById("board");
  let rows = [...board.children];
  let before = rows.map((row) => row.offsetTop);

  for (let g of [9, 10, 11, 12].sort((a, b) => counts[b] - counts[a])) {
    board.appendChild(document.getElementById("grade-" + g));
  }

  rows.forEach((row, i) => {
    let diff = before[i] - row.offsetTop;
    row.animate([{ transform: `translateY(${diff}px)` }, { transform: "none" }], 400);
  });
}

document.addEventListener("keydown", function (event) {
  if (event.key === "1") addPoint(9);
  if (event.key === "2") addPoint(10);
  if (event.key === "3") addPoint(11);
  if (event.key === "4") addPoint(12);
});
