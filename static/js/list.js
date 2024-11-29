function selectChallenges(_event) {
  let _checked = document.getElementsByClassName("form-check-input")[0].checked
  Array.prototype.forEach.call(document.getElementsByClassName("form-check-input"), (chal) => {
      if (chal.dataset.challengeId) chal.checked = _checked
  });
}

function deleteSelectedChallenges(_event) {
  let challengeIDs = []
  Array.prototype.forEach.call(document.getElementsByClassName("form-check-input"), (chal) => {
      if (chal.dataset.challengeId && chal.checked)
          challengeIDs.push(chal.dataset.challengeId)
  });
  let target = challengeIDs.length === 1 ? "challenge" : "challenges";

  CTFd.ui.ezq.ezQuery({
    title: "Delete Challenges",
    body: `Are you sure you want to delete ${challengeIDs.length} ${target}?`,
    success: function () {
      const reqs = [];
      for (var chalID of challengeIDs) {
        reqs.push(
          CTFd.fetch(`/api/v1/challenges/${chalID}`, {
            method: "DELETE",
          }),
        );
      }
      Promise.all(reqs).then((_responses) => {
        window.location.reload();
      });
    },
  });
}

function bulkEditChallenges(_event) {
  let challengeIDs = []
  Array.prototype.forEach.call(document.getElementsByClassName("form-check-input"), (chal) => {
      if (chal.dataset.challengeId && chal.checked)
          challengeIDs.push(chal.dataset.challengeId)
  });

  CTFd.ui.ezq.ezAlert({
    title: "Edit Challenges",
    body: $(`
    <form id="challenges-bulk-edit">
      <div class="form-group">
        <label>Category</label>
        <input type="text" name="category" data-initial="" value="">
      </div>
      <div class="form-group">
        <label>Value</label>
        <input type="number" name="value" data-initial="" value="">
      </div>
      <div class="form-group">
        <label>State</label>
        <select name="state" data-initial="">
          <option value="">--</option>
          <option value="visible">Visible</option>
          <option value="hidden">Hidden</option>
        </select>
      </div>
      <div class="form-group">
        <label>Solution</label>
        <select name="solution_state" data-initial="">
          <option value="">--</option>
          <option value="visible">Visible</option>
          <option value="solved">Solved</option>
          <option value="hidden">Hidden</option>
        </select>
      </div>
    </form>
    `),
    button: "Submit",
    success: function () {
      let data = $("#challenges-bulk-edit").serializeJSON(true);
      const reqs = [];
      for (var chalID of challengeIDs) {
        reqs.push(
          CTFd.fetch(`/api/v1/challenges/${chalID}`, {
            method: "PATCH",
            body: JSON.stringify(data),
          }),
        );
      }


      Promise.all(reqs).then((_responses) => {
        window.location.reload();
      });
    },
  });
}

document.getElementsByClassName("form-check-input")[0].addEventListener("click", selectChallenges);
document.getElementById("challenges-delete-button").addEventListener("click", deleteSelectedChallenges);
document.getElementById("challenges-edit-button").addEventListener("click", bulkEditChallenges);
