
$("#solution-update-container > form").submit(function (event) {
  event.preventDefault();
  const params = $(event.target).serializeJSON(true);

  CTFd.fetch("/api/v1/solutions/" + window.CHALLENGE_ID, {
    method: "PATCH",
    credentials: "same-origin",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
    },
    body: JSON.stringify(params),
  }).then((response) => {
    return response.json();
  }).then((response) => {
    if (response.success) {
      CTFd.ui.ezq.ezToast({
        title: "Success",
        body: "Your challenge has been updated!",
      });
    }
  });
});
