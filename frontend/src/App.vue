<template>
  <div id="app">
    <nav>
      <router-link to="/">Home</router-link> |
      <router-link to="/test-suites">Test Suites</router-link> |
      <router-link to="/test-cases">Test Cases</router-link> |
      <router-link to="/test-runs">Test Runs</router-link> |
      <router-link to="/test-run-templates">Test Run Templates</router-link> |
      <router-link to="/reports">Reports</router-link> |
      <router-link to="/schema">Database Schema</router-link>
    </nav>
    <router-view/>
  </div>
</template>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}

nav {
  padding: 30px;
}

nav a {
  font-weight: bold;
  color: #2c3e50;
  text-decoration: none;
  margin: 0 10px;
}

nav a.router-link-exact-active {
  color: #42b983;
}
</style>
