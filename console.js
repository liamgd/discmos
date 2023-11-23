const interval = 100;

let handleElement = (element) => {
  const id = element.getAttribute("data-id");
  if (!ids.has(id) && id) {
    const name = element.getAttribute("data-name");
    const server = element.firstChild
      .getAttribute("aria-label")
      .match(/(?<=^:.*: from ).*$/)[0];

    ids.add(id);
    servers.add(server);
    emojis.push({
      id: id,
      name: name,
      server: server,
    });
    console.log(`Registered emoji "${name}" of server "${server}"`);
  }
};

let updateEmojis = () =>
  document.querySelectorAll('button[data-type="emoji"]').forEach(handleElement);

let removeDownload = (a, url) => {
  document.body.removeChild(a);
  window.URL.revokeObjectURL(url);
};

// Modified from https://stackoverflow.com/questions/13405129/create-and-save-a-file-with-javascript
let download = (data, filename, type) => {
  const file = new Blob([data], { type: type });
  if (window.navigator.msSaveOrOpenBlob) {
    window.navigator.msSaveOrOpenBlob(file, filename);
  } else {
    const a = document.createElement("a");
    const url = URL.createObjectURL(file);
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    setTimeout(removeDownload, 0, a, url);
  }
};

let save = () => {
  clearInterval(updateId);

  console.log("Saving emoji data");
  const emojiData = {
    servers: servers,
    emojis: emojis,
  };
  const json = JSON.stringify(emojiData, null, 2).replace(/[^\x00-\x7F]/g, ".");
  download(json, "emoji-data.json", "json");
};

let emojis = [];
let ids = new Set();
let servers = new Set();

console.log(
  '%cAfter all custom emojis are registered, press any key in Discord or type "save()" in the console to save.',
  "color: orchid; font-weight: bold; font-size: 20px;"
);
const updateId = setInterval(updateEmojis);
document.body.addEventListener("keypress", save, { once: true });
