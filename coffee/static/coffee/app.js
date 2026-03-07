const API = '/api';
const TOKEN_KEY = 'coffee_auth_token';

const state = {
  currentUser: null,
  beans: [],
  recipes: [],
};

function getPageId() {
  return document.body.dataset.page || '';
}

function getRecipeIdFromPage() {
  const raw = document.body.dataset.recipeId;
  return raw ? Number(raw) : null;
}

function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
}

function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

function authHeaders() {
  const token = getToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

function getCookie(name) {
  const cookieValue = document.cookie
    .split('; ')
    .find((item) => item.startsWith(`${name}=`));
  return cookieValue ? decodeURIComponent(cookieValue.split('=')[1]) : null;
}

function csrfHeaders() {
  const csrfToken = getCookie('csrftoken');
  return csrfToken ? { 'X-CSRFToken': csrfToken } : {};
}

function stars(rating) {
  const value = Number(rating || 0);
  return '★'.repeat(value) + '☆'.repeat(5 - value);
}

async function apiGet(path) {
  const response = await fetch(`${API}${path}`, {
    credentials: 'same-origin',
    headers: { ...authHeaders() },
  });
  if (!response.ok) throw new Error(await extractApiError(response, `GET ${path} failed`));
  return response.json();
}

async function extractApiError(response, fallbackMessage) {
  try {
    const data = await response.json();
    if (typeof data.detail === 'string' && data.detail.trim()) {
      return data.detail;
    }
    if (Array.isArray(data.detail) && data.detail.length > 0) {
      return String(data.detail[0]);
    }
    const firstKey = Object.keys(data)[0];
    if (firstKey) {
      const value = data[firstKey];
      if (Array.isArray(value) && value.length > 0) {
        return String(value[0]);
      }
      if (typeof value === 'string' && value.trim()) {
        return value;
      }
    }
  } catch {
    try {
      const text = await response.text();
      if (text && text.trim()) {
        return text;
      }
    } catch {
    }
  }
  return fallbackMessage;
}

async function apiPost(path, payload) {
  const response = await fetch(`${API}${path}`, {
    method: 'POST',
    credentials: 'same-origin',
    headers: { 'Content-Type': 'application/json', ...authHeaders(), ...csrfHeaders() },
    body: JSON.stringify(payload),
  });
  if (!response.ok) throw new Error(await extractApiError(response, `POST ${path} failed`));
  return response.json();
}

async function apiDelete(path) {
  const response = await fetch(`${API}${path}`, {
    method: 'DELETE',
    credentials: 'same-origin',
    headers: { ...authHeaders(), ...csrfHeaders() },
  });
  if (!response.ok) throw new Error(await extractApiError(response, `DELETE ${path} failed`));
}

async function apiPatch(path, payload) {
  const response = await fetch(`${API}${path}`, {
    method: 'PATCH',
    credentials: 'same-origin',
    headers: { 'Content-Type': 'application/json', ...authHeaders(), ...csrfHeaders() },
    body: JSON.stringify(payload),
  });
  if (!response.ok) throw new Error(await extractApiError(response, `PATCH ${path} failed`));
  return response.json();
}

function setTopbarUser() {
  const authUser = document.getElementById('auth-user');
  const logoutBtn = document.getElementById('logout-btn');
  if (!authUser || !logoutBtn) return;

  if (state.currentUser) {
    authUser.textContent = `${state.currentUser.username} (#${state.currentUser.id})`;
    logoutBtn.style.display = 'inline-block';
  } else {
    authUser.textContent = 'Not signed in';
    logoutBtn.style.display = 'none';
  }
}

function requireAuth() {
  if (!state.currentUser) {
    window.location.href = '/auth/';
    return false;
  }
  return true;
}

async function loadCurrentUser() {
  const token = getToken();
  if (!token) {
    state.currentUser = null;
    setTopbarUser();
    return;
  }

  try {
    const data = await apiGet('/auth/me/');
    state.currentUser = data.user;
  } catch {
    state.currentUser = null;
    clearToken();
  }
  setTopbarUser();
}

function setupLogout() {
  const logoutBtn = document.getElementById('logout-btn');
  if (!logoutBtn) return;

  logoutBtn.addEventListener('click', async () => {
    try {
      await apiPost('/auth/logout/', {});
    } catch {
    }
    clearToken();
    state.currentUser = null;
    setTopbarUser();
    window.location.href = '/auth/';
  });
}

async function initAuthPage() {
  if (state.currentUser) {
    window.location.href = '/recipes/';
    return;
  }

  const loginForm = document.getElementById('login-form');

  loginForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const message = document.getElementById('login-message');
    try {
      const data = await apiPost('/auth/login/', {
        username: document.getElementById('login-username').value,
        password: document.getElementById('login-password').value,
      });
      setToken(data.token);
      message.textContent = 'Login successful.';
      window.location.href = '/recipes/';
    } catch (error) {
      message.textContent = error.message || 'Login failed. Check credentials.';
    }
  });
}

async function initRegisterPage() {
  if (state.currentUser) {
    window.location.href = '/recipes/';
    return;
  }

  const registerForm = document.getElementById('register-form');

  registerForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const message = document.getElementById('register-message');
    const username = document.getElementById('register-username').value.trim();
    const email = document.getElementById('register-email').value.trim();
    const password = document.getElementById('register-password').value;

    if (!username || !email || !password) {
      message.textContent = 'Please fill in username, email, and password.';
      return;
    }

    try {
      const data = await apiPost('/auth/register/', {
        username,
        email,
        password,
      });
      setToken(data.token);
      message.textContent = 'Account created successfully.';
      window.location.href = '/recipes/';
    } catch (error) {
      message.textContent = error.message || 'Account creation failed.';
    }
  });
}

async function initBeansPage() {
  state.beans = await apiGet('/beans/');

  const originFilter = document.getElementById('origin-filter');
  const roastFilter = document.getElementById('roast-filter');
  const beanList = document.getElementById('bean-list');

  const origins = [...new Set(state.beans.map((bean) => bean.origin).filter(Boolean))].sort();
  const roasts = [...new Set(state.beans.map((bean) => bean.roast_level).filter(Boolean))].sort();

  origins.forEach((origin) => {
    originFilter.insertAdjacentHTML('beforeend', `<option value="${origin}">${origin}</option>`);
  });
  roasts.forEach((roast) => {
    roastFilter.insertAdjacentHTML('beforeend', `<option value="${roast}">${roast}</option>`);
  });

  const render = async () => {
    const params = new URLSearchParams();
    if (originFilter.value) params.set('origin', originFilter.value);
    if (roastFilter.value) params.set('roast_level', roastFilter.value);
    const beans = await apiGet(`/beans/${params.toString() ? `?${params.toString()}` : ''}`);

    beanList.innerHTML = '';
    beans.forEach((bean) => {
      const tags = (bean.flavour_tags || '')
        .split(/[;,]/)
        .map((tag) => tag.trim())
        .filter(Boolean)
        .map((tag) => `<span class="tag">${tag}</span>`)
        .join('');

      beanList.insertAdjacentHTML(
        'beforeend',
        `<article class="card">
          <h3>${bean.name}</h3>
          <p><strong>Origin:</strong> ${bean.origin || 'N/A'}</p>
          <p><strong>Roast:</strong> ${bean.roast_level || 'N/A'}</p>
          <div class="tags">${tags || '<span class="tag">No flavour tags</span>'}</div>
        </article>`
      );
    });
  };

  document.getElementById('apply-bean-filter').addEventListener('click', render);
  await render();
}

async function initRecipesPage() {
  const recipeFeed = document.getElementById('recipe-feed');
  const recipes = await apiGet('/recipes/?is_public=true');
  let favouriteRecipeIds = new Set();

  if (state.currentUser) {
    const favourites = await apiGet(`/favourites/?user=${state.currentUser.id}`);
    favouriteRecipeIds = new Set(favourites.map((item) => item.recipe));
  }

  const toggleFavourite = async (recipeId) => {
    if (!state.currentUser) {
      window.location.href = '/auth/';
      return;
    }

    const existing = await apiGet(`/favourites/?user=${state.currentUser.id}&recipe=${recipeId}`);
    if (existing.length > 0) {
      await apiDelete(`/favourites/${existing[0].id}/`);
    } else {
      await apiPost('/favourites/', { recipe: recipeId });
    }
    await initRecipesPage();
  };

  recipeFeed.innerHTML = '';
  recipes.forEach((recipe) => {
    const isFavourited = favouriteRecipeIds.has(recipe.id);
    recipeFeed.insertAdjacentHTML(
      'beforeend',
      `<article class="card">
        <h3>Recipe #${recipe.id}</h3>
        <p><strong>Method:</strong> ${recipe.method || 'N/A'}</p>
        <p><strong>Grind:</strong> ${recipe.grind_size || 'N/A'}</p>
        <p><strong>Water Temp:</strong> ${recipe.water_temp || 'N/A'}</p>
        <p><strong>Brew Time:</strong> ${recipe.brew_time || 'N/A'}</p>
        <p><strong>Bean:</strong> ${recipe.bean_name || `Bean #${recipe.bean || 'N/A'}`}</p>
        <div class="inline-actions">
          <a class="tab" href="/recipes/${recipe.id}/">View Details</a>
          <button data-fav-id="${recipe.id}">${isFavourited ? 'Unfavourite' : 'Favourite'}</button>
        </div>
      </article>`
    );
  });

  recipeFeed.querySelectorAll('[data-fav-id]').forEach((button) => {
    button.addEventListener('click', () => toggleFavourite(Number(button.dataset.favId)));
  });
}

async function initRecipeDetailPage() {
  const recipeId = getRecipeIdFromPage();
  if (!recipeId) return;

  const recipe = await apiGet(`/recipes/${recipeId}/`);
  const reviews = await apiGet(`/reviews/?recipe=${recipeId}`);
  const average = reviews.length
    ? (reviews.reduce((sum, item) => sum + Number(item.rating || 0), 0) / reviews.length).toFixed(2)
    : 'N/A';

  const recipeDetail = document.getElementById('recipe-detail');
  recipeDetail.innerHTML = `
    <article class="card">
      <h3>Recipe #${recipe.id}</h3>
      <p><strong>Method:</strong> ${recipe.method || 'N/A'}</p>
      <p><strong>Bean:</strong> ${recipe.bean_name || `Bean #${recipe.bean || 'N/A'}`}</p>
      <p><strong>Water Temp:</strong> ${recipe.water_temp || 'N/A'}</p>
      <p><strong>Grind Size:</strong> ${recipe.grind_size || 'N/A'}</p>
      <p><strong>Brew Time:</strong> ${recipe.brew_time || 'N/A'}</p>
      <p><strong>Description:</strong> ${recipe.description || 'N/A'}</p>
      <p><strong>Average Rating:</strong> ${average}</p>
      <h4>Reviews</h4>
      <div id="review-list"></div>
      <h4>Leave a Review</h4>
      <form id="review-form" class="form-grid">
        <input id="review-rating" type="number" min="1" max="5" placeholder="Rating 1-5" required />
        <textarea id="review-comment" placeholder="Comment"></textarea>
        <button type="submit">Submit Review</button>
      </form>
      <p id="review-message" class="message"></p>
    </article>
  `;

  const reviewList = document.getElementById('review-list');
  reviewList.innerHTML = reviews.length
    ? reviews
        .map((review) => `<div class="card"><div class="stars">${stars(review.rating)}</div><p>${review.comment || ''}</p></div>`)
        .join('')
    : '<p>No reviews yet.</p>';

  document.getElementById('review-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    if (!requireAuth()) return;

    const message = document.getElementById('review-message');
    try {
      await apiPost('/reviews/', {
        recipe: recipeId,
        rating: Number(document.getElementById('review-rating').value),
        comment: document.getElementById('review-comment').value,
      });
      message.textContent = 'Review submitted.';
      await initRecipeDetailPage();
    } catch {
      message.textContent = 'Review failed.';
    }
  });
}

async function initCreateRecipePage() {
  if (!requireAuth()) return;

  const beans = await apiGet('/beans/');
  const beanSelect = document.getElementById('recipe-bean');
  beans.forEach((bean) => {
    beanSelect.insertAdjacentHTML('beforeend', `<option value="${bean.id}">${bean.name} (${bean.origin || 'Unknown'})</option>`);
  });

  document.getElementById('create-recipe-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    const message = document.getElementById('create-recipe-message');
    try {
      await apiPost('/recipes/', {
        bean: Number(document.getElementById('recipe-bean').value),
        method: document.getElementById('recipe-method').value,
        water_temp: Number(document.getElementById('recipe-water-temp').value),
        grind_size: document.getElementById('recipe-grind-size').value,
        brew_time: Number(document.getElementById('recipe-brew-time').value),
        description: document.getElementById('recipe-description').value,
        is_public: document.getElementById('recipe-public').checked,
      });
      message.textContent = 'Recipe created successfully.';
    } catch {
      message.textContent = 'Failed to create recipe.';
    }
  });
}

async function initLogBrewPage() {
  if (!requireAuth()) return;

  const recipes = await apiGet('/recipes/?is_public=true');
  const recipeSelect = document.getElementById('brew-recipe');
  const logList = document.getElementById('brew-log-list');

  const recipeNameById = new Map();
  recipes.forEach((recipe) => {
    recipeNameById.set(recipe.id, `#${recipe.id} ${recipe.method || 'Unknown'} (${recipe.bean_name || 'No bean'})`);
    recipeSelect.insertAdjacentHTML(
      'beforeend',
      `<option value="${recipe.id}">#${recipe.id} ${recipe.method || 'Unknown'} (${recipe.bean_name || 'No bean'})</option>`
    );
  });

  const renderBrewLogs = async () => {
    const brews = await apiGet(`/brews/?user=${state.currentUser.id}`);
    logList.innerHTML = '';

    if (brews.length === 0) {
      logList.innerHTML = '<tr><td colspan="8">No brew logs yet.</td></tr>';
      return;
    }

    brews.forEach((brew) => {
      logList.insertAdjacentHTML(
        'beforeend',
        `<tr>
          <td>${brew.id}</td>
          <td>${recipeNameById.get(brew.recipe) || `#${brew.recipe}`}</td>
          <td>${brew.brewed_at ? new Date(brew.brewed_at).toLocaleString() : 'N/A'}</td>
          <td>${brew.actual_temp ?? 'N/A'}</td>
          <td>${brew.actual_time ?? 'N/A'}</td>
          <td>${brew.rating ?? 'N/A'}</td>
          <td>${brew.notes || 'N/A'}</td>
          <td>
            <div class="inline-actions table-actions">
              <button class="secondary" data-edit-brew-id="${brew.id}">Edit</button>
              <button data-delete-brew-id="${brew.id}">Delete</button>
            </div>
          </td>
        </tr>`
      );
    });

    logList.querySelectorAll('[data-edit-brew-id]').forEach((button) => {
      button.addEventListener('click', async () => {
        const brewId = Number(button.dataset.editBrewId);
        const actualTempInput = window.prompt('New Actual Temp:');
        const actualTimeInput = window.prompt('New Actual Time (seconds):');
        const ratingInput = window.prompt('New Rating (1-5):');
        const notesInput = window.prompt('New Notes (optional):') ?? '';

        if (!actualTempInput || !actualTimeInput || !ratingInput) {
          return;
        }

        try {
          await apiPatch(`/brews/${brewId}/`, {
            actual_temp: Number(actualTempInput),
            actual_time: Number(actualTimeInput),
            rating: Number(ratingInput),
            notes: notesInput,
          });
          await renderBrewLogs();
        } catch (error) {
          window.alert(error.message || 'Failed to update brew log.');
        }
      });
    });

    logList.querySelectorAll('[data-delete-brew-id]').forEach((button) => {
      button.addEventListener('click', async () => {
        const brewId = Number(button.dataset.deleteBrewId);
        if (!window.confirm('Delete this brew log?')) return;

        try {
          await apiDelete(`/brews/${brewId}/`);
          await renderBrewLogs();
        } catch (error) {
          window.alert(error.message || 'Failed to delete brew log.');
        }
      });
    });
  };

  document.getElementById('log-brew-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    const message = document.getElementById('log-brew-message');
    try {
      await apiPost('/brews/', {
        recipe: Number(document.getElementById('brew-recipe').value),
        actual_temp: Number(document.getElementById('brew-actual-temp').value),
        actual_time: Number(document.getElementById('brew-actual-time').value),
        rating: Number(document.getElementById('brew-rating').value),
        notes: document.getElementById('brew-notes').value,
      });
      message.textContent = 'Brew logged successfully.';
      await renderBrewLogs();
    } catch {
      message.textContent = 'Failed to log brew.';
    }
  });

  await renderBrewLogs();
}

async function initAnalyticsPage() {
  const data = await apiGet('/analytics/summary/');

  const methodContainer = document.getElementById('popular-methods');
  methodContainer.innerHTML = '';
  const maxMethod = Math.max(1, ...data.popular_methods.map((item) => item.count));
  data.popular_methods.forEach((item) => {
    const width = (item.count / maxMethod) * 100;
    methodContainer.insertAdjacentHTML(
      'beforeend',
      `<div class="bar-row"><div class="bar-label">${item.method} (${item.count})</div><div class="bar" style="width:${width}%"></div></div>`
    );
  });

  const originContainer = document.getElementById('ratings-by-origin');
  originContainer.innerHTML = '';
  data.average_ratings_by_origin.forEach((item) => {
    const width = (Number(item.avg_rating || 0) / 5) * 100;
    originContainer.insertAdjacentHTML(
      'beforeend',
      `<div class="bar-row"><div class="bar-label">${item.origin} (${item.avg_rating ?? 'N/A'})</div><div class="bar" style="width:${width}%"></div></div>`
    );
  });

  const favouriteContainer = document.getElementById('most-favourited');
  favouriteContainer.innerHTML = '';
  data.most_favourited_recipes.forEach((item) => {
    favouriteContainer.insertAdjacentHTML(
      'beforeend',
      `<li>Recipe #${item.id} • ${item.method || 'N/A'} • favourites: ${item.favourites_count} • avg rating: ${item.average_rating ?? 'N/A'}</li>`
    );
  });
}

async function initUserPage() {
  if (!requireAuth()) return;

  const profileDetails = document.getElementById('user-profile-details');
  const favouritesList = document.getElementById('user-favourites-list');

  profileDetails.innerHTML = `
    <p><strong>ID:</strong> ${state.currentUser.id}</p>
    <p><strong>Username:</strong> ${state.currentUser.username}</p>
    <p><strong>Email:</strong> ${state.currentUser.email}</p>
    <p><strong>Created At:</strong> ${state.currentUser.created_at ? new Date(state.currentUser.created_at).toLocaleString() : 'N/A'}</p>
  `;

  const favourites = await apiGet(`/favourites/?user=${state.currentUser.id}`);
  favouritesList.innerHTML = '';

  if (favourites.length === 0) {
    favouritesList.innerHTML = '<p>No favourited recipes yet.</p>';
    return;
  }

  const uniqueRecipeIds = [...new Set(favourites.map((item) => item.recipe))];
  const recipes = await Promise.all(uniqueRecipeIds.map((recipeId) => apiGet(`/recipes/${recipeId}/`)));

  recipes.forEach((recipe) => {
    favouritesList.insertAdjacentHTML(
      'beforeend',
      `<article class="card">
        <h4>Recipe #${recipe.id}</h4>
        <p><strong>Method:</strong> ${recipe.method || 'N/A'}</p>
        <p><strong>Bean:</strong> ${recipe.bean_name || `Bean #${recipe.bean || 'N/A'}`}</p>
        <p><strong>Created At:</strong> ${recipe.created_at ? new Date(recipe.created_at).toLocaleString() : 'N/A'}</p>
        <a class="tab" href="/recipes/${recipe.id}/">View Recipe</a>
      </article>`
    );
  });
}

async function bootstrap() {
  await loadCurrentUser();
  setupLogout();

  const page = getPageId();
  if (page === 'auth') await initAuthPage();
  if (page === 'register') await initRegisterPage();
  if (page === 'beans') await initBeansPage();
  if (page === 'recipes') await initRecipesPage();
  if (page === 'detail') await initRecipeDetailPage();
  if (page === 'create') await initCreateRecipePage();
  if (page === 'brew') await initLogBrewPage();
  if (page === 'analytics') await initAnalyticsPage();
  if (page === 'user') await initUserPage();
}

bootstrap();
