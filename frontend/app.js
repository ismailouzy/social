const API_URL = "http://127.0.0.1:8000/graphql/";
let token = localStorage.getItem("jwt") || null;

// Load posts
async function loadPosts() {
  const query = `query {
  posts {
    id
    content
    likeCount
    comments {
      text
      user { username }
    }
  }
}`;
  const res = await fetch(API_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query }),
  });
  const data = await res.json();
  displayPosts(data.data.posts);
}

function displayPosts(posts) {
  const feed = document.getElementById("feed");
  feed.innerHTML = "";
  posts.forEach(p => {
    let commentsHtml = "";
    if (p.comments) {
      p.comments.forEach(c => {
        commentsHtml += `<div class="comment"><b>${c.user.username}:</b> ${c.text}</div>`;
      });
    }

    feed.innerHTML += `
      <div class="post">
        <p>${p.content}</p>
        <small>Likes: ${p.likeCount}</small><br>
        <button onclick="likePost(${p.id})">❤️ Like</button>

        <div class="comments">${commentsHtml}</div>
        ${token ? `<input id="c${p.id}" type="text" placeholder="Write a comment">
        <button onclick="addComment(${p.id})">💬 Comment</button>` : ""}
      </div>`;
  });
}

async function likePost(postId) {
	if (!token)
	{
		alert("Login required to like!");
		return;
	}

	const mutation = `
	mutation {
		likePost(postId: ${postId}) {
			post { id likeCount }
		}
	}`;
	await fetch(API_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": "JWT " + token
    },
    body: JSON.stringify({ query: mutation }),
  });

  loadPosts(); // reload feed
	
}

// Login and store token
async function login() {
  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;

  const mutation = `
    mutation {
      tokenAuth(username: "${username}", password: "${password}") {
        token
      }
    }`;

  const res = await fetch(API_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query: mutation }),
  });
  const data = await res.json();

  if (data.data && data.data.tokenAuth.token) {
    token = data.data.tokenAuth.token;
    localStorage.setItem("jwt", token);
    document.getElementById("create-section").style.display = "block";
    alert("Login successful!");
  } else {
    alert("Login failed!");
  }
	function showUser(username) {
	  document.getElementById("current-user").textContent = username;
	  document.getElementById("user-section").style.display = "block";
	  document.getElementById("create-section").style.display = "block";
	  document.getElementById("login-section").style.display = "none";
	}

	function logout() {
	  localStorage.removeItem("jwt");
	  token = null;
	  document.getElementById("user-section").style.display = "none";
	  document.getElementById("create-section").style.display = "none";
	  document.getElementById("login-section").style.display = "block";
	  alert("Logged out!");
	}

	// After successful login:
	if (data.data.tokenAuth.token) {
		token = data.data.tokenAuth.token;
		localStorage.setItem("jwt", token);
		showUser(username);
		alert("Login successful!");
	}

}

// Create post (requires JWT)
async function createPost() {
  const content = document.getElementById("postContent").value;
  const mutation = `mutation { createPost(content:"${content}") { post { id content } } }`;

  const res = await fetch(API_URL, {
    method: "POST",
    headers: { 
      "Content-Type": "application/json",
      "Authorization": "JWT " + token 
    },
    body: JSON.stringify({ query: mutation }),
  });
  const data = await res.json();

  if (data.errors) {
    alert("You must be logged in to post!");
  } else {
    document.getElementById("postContent").value = "";
    loadPosts();
  }
}


async function addComment(postId) {
  const text = document.getElementById("c" + postId).value;
  if (!text) return;

  const mutation = `
    mutation {
      createComment(postId: ${postId}, text: "${text}") {
        comment { id text user { username } }
      }
    }`;

  await fetch(API_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": "JWT " + token
    },
    body: JSON.stringify({ query: mutation }),
  });

  loadPosts(); // refresh feed
}


loadPosts();

