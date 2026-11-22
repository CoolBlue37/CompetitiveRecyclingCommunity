import { supabase } from './supabaseClient.js'

const { data, error } = await supabase.rpc('get_stats');
if (error) {
  console.error(error)
} else {
  console.log(data)
}

const { data: lastEntry, error: lastError } = await supabase
  .from('posts')
  .select('success, grade')
  .order('created_at', { ascending: false })
  .limit(1)
  .maybeSingle()

if (lastError) {
  console.error(lastError)
} else if (!lastEntry) {
  console.log("No entries yet")
}
else {
  console.log(lastEntry.success, lastEntry.grade)
}

let correct = { 9: data[0].success, 10: data[1].success, 11: data[2].success, 12: data[3].success };
let total = { 9: data[0].total_trash, 10: data[1].total_trash, 11: data[2].total_trash, 12: data[3].total_trash };
let grades = [9, 10, 11, 12];
let categories = ["cardboard", "glass", "metal", "misc", "organic", "paper", "plastic"];

function render(data) {
  
  let allItems = total[9] + total[10] + total[11] + total[12];
  document.getElementById("total").textContent = allItems;
  
  for (let g of grades) {
    let row = document.getElementById("grade-" + g);
    row.querySelector(".count").textContent = percent(g) + "%";
    row.querySelector(".detail").textContent = correct[g] + "/" + total[g];
    row.querySelector(".fill").style.width = percent(g) + "%";
    for (let c of categories) {
      let box = document.getElementById(g + "-" + c);
      box.textContent = data[g-9][c];
    }
  }

  if (lastEntry) {
    if (lastEntry.success) {
      document.getElementById("message").textContent =
        "Nice sorting, " + lastEntry.grade + "th grade!";
    } else {
      document.getElementById("message").textContent =
        "Oops, wrong bin, " + lastEntry.grade + "th grade!";
    }
  }

  sortBoard();
}

function percent(grade) {
  if (total[grade] === 0) {
    return 0;
  }
  return Math.round((correct[grade] / total[grade]) * 100);
}

render();

// function recordResult(grade, wasCorrect) {
//   total[grade] = total[grade] + 1;
//   if (wasCorrect) {
//     correct[grade] = correct[grade] + 1;
//   }

//   if (category !== "") {
//     let box = document.getElementById(grade + "-" + category);
//     box.textContent = Number(box.textContent) + 1;
//     category = "";
//   }

//   let allItems = total[9] + total[10] + total[11] + total[12];
//   document.getElementById("total").textContent = allItems;

//   if (wasCorrect) {
//     document.getElementById("message").textContent =
//       "Nice sorting, " + grade + "th grade!";
//   } else {
//     document.getElementById("message").textContent =
//       "Oops, wrong bin, " + grade + "th grade!";
//   }

  // for (let g of grades) {
//     let row = document.getElementById("grade-" + g);
//     row.querySelector(".count").textContent = percent(g) + "%";
//     row.querySelector(".detail").textContent = correct[g] + "/" + total[g];
//     row.querySelector(".fill").style.width = percent(g) + "%";
//   }

//   sortBoard();

//   let row = document.getElementById("grade-" + grade);
//   if (wasCorrect) {
//     row.classList.add("pop");
//   } else {
//     row.classList.add("wrong");
//   }
//   setTimeout(() => {
//     row.classList.remove("pop");
//     row.classList.remove("wrong");
//   }, 300);
// }

function sortBoard() {
  let board = document.getElementById("board");
  grades.sort((a, b) => percent(b) - percent(a));
  for (let g of grades) {
    board.appendChild(document.getElementById("grade-" + g));
  }
}

// document.addEventListener("keydown", (event) => {
//   if (event.key === "a") category = "organic";
//   if (event.key === "s") category = "miscellaneous";
//   if (event.key === "d") category = "paper";
//   if (event.key === "f") category = "cardboard";
//   if (event.key === "g") category = "plastic";
//   if (event.key === "h") category = "metal";

//   if (event.key === "1") recordResult(9, true);
//   if (event.key === "2") recordResult(10, true);
//   if (event.key === "3") recordResult(11, true);
//   if (event.key === "4") recordResult(12, true);
//   if (event.key === "q") recordResult(9, false);
//   if (event.key === "w") recordResult(10, false);
//   if (event.key === "e") recordResult(11, false);
//   if (event.key === "r") recordResult(12, false);
// });
