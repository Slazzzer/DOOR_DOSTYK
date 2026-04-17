<template>
  <div id="app">
    <header class="header">
      <h1>Дверной Достык</h1>
      <nav>
        <router-link to="/orders">Оформление заказа</router-link>
        <router-link to="/shipments">Приёмка товара</router-link>
      </nav>
    </header>
    <main class="main">
      <router-view v-slot="{ Component }">
        <keep-alive>
          <component :is="Component" />
        </keep-alive>
      </router-view>
    </main>
  </div>
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
  background: #f0f2f5;
  color: #1a1a2e;
}

.header {
  background: #1a1a2e;
  color: #fff;
  padding: 16px 32px;
  display: flex;
  align-items: center;
  gap: 32px;
}

.header h1 {
  font-size: 20px;
  font-weight: 600;
}

.header nav {
  display: flex;
  gap: 16px;
}

.header nav a {
  color: #a0aec0;
  text-decoration: none;
  padding: 6px 14px;
  border-radius: 6px;
  transition: all 0.2s;
}

.header nav a:hover {
  color: #fff;
  background: rgba(255, 255, 255, 0.1);
}

.header nav a.router-link-active {
  color: #fff;
  background: #3b82f6;
}

.main {
  max-width: 900px;
  margin: 32px auto;
  padding: 0 16px;
}
</style>
