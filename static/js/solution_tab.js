async function setupSolution(id) {
  CTFd.fetch("/api/v1/solutions/" + id, {
    method: "GET",
    credentials: "same-origin",
    headers: {"Accept": "application/json",},
  }).then((response) => {
    return response.json();
  }).then((response) => {
    if (response && response.success && response.data.solution_html) {
      document.getElementById("solution-html").innerHTML = response.data.solution_html
      document.getElementById("solution-tab").style.display = ""
    } else {
      document.getElementById("solution-tab").style.display = "none"
    }
  }).catch(() => {
    document.getElementById("solution-tab").style.display = "none"
  });
}

async function showSolution() {
  // Can't access bootstrap here, so do what "Tab($this).show()" would have done
  // Only called for core-beta theme
  let vals = document.getElementById("solution-tab").parentElement.getElementsByClassName("nav-link");
  for (let i = 0; i < vals.length; i++) {
    vals.item(i).classList.remove("active");
  }
  document.getElementById("solution-tab").getElementsByClassName("nav-link")[0].classList.add("active");
  vals = document.getElementById("solution").parentElement.getElementsByClassName("tab-pane")
  for (let i = 0; i < vals.length; i++) {
    vals.item(i).classList.remove("active", "show");
  }
  document.getElementById("solution").classList.add("show","active");
}

try {
  // JQuery version used by the core theme
  $(document).on('shown.bs.modal','#challenge-window', (event) => {
    id = document.getElementById("solution-tab").getAttribute("value");
    setupSolution(id);
  });
} catch {
  document.addEventListener("shown.bs.modal", (event) => {
    if (event.target.id === 'challenge-window') {
      id = document.getElementById("solution-tab").getAttribute("value")
      setupSolution(id);
    }
  });
}

