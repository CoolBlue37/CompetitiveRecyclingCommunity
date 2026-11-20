let correct = { 9: 0, 10: 0, 11: 0, 12: 0 };
let total = { 9: 0, 10: 0, 11: 0, 12: 0 };
let grades = [9, 10, 11, 12];

function percent(grade) {
  if (total[grade] === 0) {
    return 0;
  }
  return Math.round((correct[grade] / total[grade]) * 100);
}

function recordResult(grade, wasCorrect) {
  total[grade] = total[grade] + 1;
  if (wasCorrect) {
    correct[grade] = correct[grade] + 1;
  }

  let allItems = 0;
  for (let g of grades) {
    allItems = allItems + total[g];
  }
  document.getElementById("total").textContent = allItems;

  if (wasCorrect) {
    document.getElementById("message").textContent =
      "Nice sorting, " + grade + "th grade!";
  } else {
    document.getElementById("message").textContent =
      "Oops, wrong bin, " + grade + "th grade!";
  }

  for (let g of grades) {
    let row = document.getElementById("grade-" + g);
    row.querySelector(".count").textContent = percent(g) + "%";
    row.querySelector(".detail").textContent = correct[g] + "/" + total[g];
    row.querySelector(".fill").style.width = percent(g) + "%";
  }

  sortBoard();

  let row = document.getElementById("grade-" + grade);
  if (wasCorrect) {
    row.classList.add("pop");
  } else {
    row.classList.add("wrong");
  }
  setTimeout(() => {
    row.classList.remove("pop");
    row.classList.remove("wrong");
  }, 300);
}

function sortBoard() {
  let board = document.getElementById("board");
  grades.sort((a, b) => {
    if (percent(b) !== percent(a)) {
      return percent(b) - percent(a);
    }
    return total[b] - total[a];
  });

  for (let g of grades) {
    board.appendChild(document.getElementById("grade-" + g));
  }
}

//   1 2 3 4 = 9th 10th 11th 12th sorted CORRECTLY
//   q w e r = 9th 10th 11th 12th sorted WRONG
document.addEventListener("keydown", (event) => {
  if (event.key === "1") recordResult(9, true);
  if (event.key === "2") recordResult(10, true);
  if (event.key === "3") recordResult(11, true);
  if (event.key === "4") recordResult(12, true);
  if (event.key === "q") recordResult(9, false);
  if (event.key === "w") recordResult(10, false);
  if (event.key === "e") recordResult(11, false);
  if (event.key === "r") recordResult(12, false);
});
