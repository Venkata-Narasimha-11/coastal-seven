// Real-Time Notification & File Upload Client

const clientId = "client_" + Math.random().toString(36).substring(2, 9);
let socket = null;
let reconnectInterval = null;

// UI Elements
const statusDot = document.getElementById("statusDot");
const statusText = document.getElementById("statusText");
const clientIdLabel = document.getElementById("clientIdLabel");
const logBox = document.getElementById("logBox");
const feedContainer = document.getElementById("feedContainer");
const galleryGrid = document.getElementById("galleryGrid");
const dropzone = document.getElementById("dropzone");
const fileInput = document.getElementById("fileInput");
const chatInput = document.getElementById("chatInput");
const sendBtn = document.getElementById("sendBtn");
const pingBtn = document.getElementById("pingBtn");
const activeCountEl = document.getElementById("activeCount");

clientIdLabel.textContent = clientId;

function log(msg) {
  const line = document.createElement("div");
  line.textContent = `[${new Date().toLocaleTimeString()}] ${msg}`;
  logBox.appendChild(line);
  logBox.scrollTop = logBox.scrollHeight;
}

// ==========================================
// WebSocket Connection Lifecycle
// ==========================================
function initWebSocket() {
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  const wsUrl = `${protocol}//${window.location.host}/ws/${clientId}`;

  log(`Connecting to WebSocket: ${wsUrl}`);
  socket = new WebSocket(wsUrl);

  socket.onopen = () => {
    statusDot.classList.add("connected");
    statusText.textContent = "Connected (Live)";
    log("✅ WebSocket Connected!");
    if (reconnectInterval) {
      clearInterval(reconnectInterval);
      reconnectInterval = null;
    }
  };

  socket.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      handleWebSocketMessage(data);
    } catch (e) {
      log("Received raw: " + event.data);
    }
  };

  socket.onclose = () => {
    statusDot.classList.remove("connected");
    statusText.textContent = "Disconnected";
    log("⚠️ WebSocket Disconnected. Reconnecting in 3s...");
    if (!reconnectInterval) {
      reconnectInterval = setInterval(initWebSocket, 3000);
    }
  };

  socket.onerror = (err) => {
    log("❌ WebSocket error occurred.");
  };
}

function handleWebSocketMessage(msg) {
  log(`[Event: ${msg.event}] from ${msg.sender_id}`);

  if (msg.event === "file_uploaded" || msg.event === "image_processed") {
    addFeedItem(msg.data);
    loadGallery();
  } else if (msg.event === "client_connected" || msg.event === "client_disconnected") {
    if (msg.data && msg.data.total_clients !== undefined) {
      activeCountEl.textContent = msg.data.total_clients;
    }
  } else if (msg.event === "chat_message") {
    log(`💬 ${msg.sender_id}: ${msg.data.message}`);
  } else if (msg.event === "heartbeat") {
    log(`💓 Heartbeat reply: ${msg.data.reply}`);
  }
}

// ==========================================
// Live Feed & Gallery Updates
// ==========================================
function addFeedItem(data) {
  const item = document.createElement("div");
  item.className = "feed-item";

  const thumbUrl = data.thumbnail_url || data.url;
  item.innerHTML = `
    <img src="${thumbUrl}" alt="Thumbnail" class="feed-thumb" onerror="this.src='https://via.placeholder.com/70?text=IMG'">
    <div class="feed-details">
      <div class="feed-title">📸 ${data.original_name || data.filename}</div>
      <div class="feed-meta">
        <span>Size: ${data.file_size_human}</span>
        <span>MIME: ${data.content_type}</span>
        <span>Proc: ${data.processing_time_ms ? data.processing_time_ms + "ms" : "N/A"}</span>
      </div>
      <div style="margin-top: 0.25rem;">
        <a href="${data.url}" target="_blank" class="btn btn-secondary" style="padding: 0.2rem 0.6rem; font-size: 0.75rem;">View Full</a>
      </div>
    </div>
  `;

  feedContainer.prepend(item);
}

async function loadGallery() {
  try {
    const res = await fetch("/api/v1/uploads");
    if (!res.ok) return;
    const files = await res.json();
    galleryGrid.innerHTML = "";

    if (files.length === 0) {
      galleryGrid.innerHTML = `<div style="grid-column: 1/-1; color: var(--text-muted); text-align: center; padding: 2rem;">No files uploaded yet. Drag an image above to get started!</div>`;
      return;
    }

    files.forEach(f => {
      const card = document.createElement("div");
      card.className = "gallery-card";
      const displayImg = f.thumbnail_url || f.url;
      card.innerHTML = `
        <img src="${displayImg}" class="gallery-img" alt="${f.filename}">
        <div class="gallery-info">
          <div style="font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${f.filename}</div>
          <div style="color: var(--text-muted); font-size: 0.75rem; margin-top: 0.25rem;">${f.size_human}</div>
          <div style="margin-top: 0.5rem; display: flex; gap: 0.5rem;">
            <a href="${f.url}" target="_blank" class="btn btn-secondary" style="padding: 0.2rem 0.5rem; font-size: 0.75rem;">Open</a>
            <button onclick="deleteFile('${f.filename}')" class="btn btn-danger" style="padding: 0.2rem 0.5rem; font-size: 0.75rem;">Delete</button>
          </div>
        </div>
      `;
      galleryGrid.appendChild(card);
    });
  } catch (err) {
    console.error("Failed to load gallery:", err);
  }
}

async function deleteFile(filename) {
  if (!confirm(`Delete ${filename}?`)) return;
  try {
    const res = await fetch(`/api/v1/uploads/${filename}`, { method: "DELETE" });
    if (res.ok) {
      log(`Deleted file: ${filename}`);
      loadGallery();
    }
  } catch (err) {
    log(`Error deleting file: ${err}`);
  }
}

// ==========================================
// File Upload & Drag-and-Drop
// ==========================================
dropzone.addEventListener("click", () => fileInput.click());

dropzone.addEventListener("dragover", (e) => {
  e.preventDefault();
  dropzone.classList.add("dragover");
});

dropzone.addEventListener("dragleave", () => {
  dropzone.classList.remove("dragover");
});

dropzone.addEventListener("drop", (e) => {
  e.preventDefault();
  dropzone.classList.remove("dragover");
  if (e.dataTransfer.files.length) {
    uploadFiles(e.dataTransfer.files);
  }
});

fileInput.addEventListener("change", () => {
  if (fileInput.files.length) {
    uploadFiles(fileInput.files);
  }
});

async function uploadFiles(files) {
  for (let file of files) {
    log(`Uploading '${file.name}' (${(file.size / 1024).toFixed(1)} KB)...`);
    const formData = new FormData();
    formData.append("file", file);
    formData.append("uploader_name", clientId);

    try {
      const response = await fetch("/api/v1/integrated/upload-notify", {
        method: "POST",
        body: formData,
      });

      const result = await response.json();
      if (response.ok) {
        log(` Uploaded successfully: ${result.filename}`);
      } else {
        log(`❌ Upload failed: ${result.message || JSON.stringify(result)}`);
      }
    } catch (err) {
      log(`❌ Network upload error: ${err}`);
    }
  }
}

// ==========================================
// Chat & Heartbeat Actions
// ==========================================
sendBtn.addEventListener("click", () => {
  const text = chatInput.value.trim();
  if (!text || !socket || socket.readyState !== WebSocket.OPEN) return;

  socket.send(JSON.stringify({
    action: "broadcast",
    message: text
  }));
  chatInput.value = "";
});

pingBtn.addEventListener("click", () => {
  if (!socket || socket.readyState !== WebSocket.OPEN) return;
  log("Sending ping to server...");
  socket.send(JSON.stringify({ action: "ping" }));
});

// Startup initialization
window.addEventListener("DOMContentLoaded", () => {
  initWebSocket();
  loadGallery();
});
