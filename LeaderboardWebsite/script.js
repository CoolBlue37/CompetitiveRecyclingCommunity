import { supabase } from './supabaseClient.js'

let total = {}
let correct = {}
let grades = [9, 10, 11, 12];
let categories = ["cardboard", "glass", "metal", "misc", "organic", "paper", "plastic"];

async function refresh() {
  const { data, error } = await supabase.rpc('get_stats');
  if (error) return console.error(error);

  const { data: lastEntry, error: lastError } = await supabase
    .from('posts')
    .select('success, grade')
    .order('created_at', { ascending: false })
    .limit(1)
    .maybeSingle()
  if (lastError) return console.error(lastError);
  
  render(data, lastEntry);
}

function render(data, lastEntry) {
  total = { 9: data[0].total_trash, 10: data[1].total_trash, 11: data[2].total_trash, 12: data[3].total_trash };
  correct = { 9: data[0].successes, 10: data[1].successes, 11: data[2].successes, 12: data[3].successes };
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

function sortBoard() {
  let board = document.getElementById("board");
  grades.sort((a, b) => percent(b) - percent(a));
  for (let g of grades) {
    board.appendChild(document.getElementById("grade-" + g));
  }
}

await refresh();

supabase
  .channel('posts-changes')
  .on(
    'postgres_changes',
    { event: 'INSERT', schema: 'public', table: 'posts' },
    (payload) => {
      refresh();
    }
  )
  .subscribe();
