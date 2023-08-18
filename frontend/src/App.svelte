<script lang="ts">
  import Router from 'svelte-spa-router'
  import routes from './routes.js'
  import 'fluent-svelte/theme.css' // Required for ProgressRing component
  let open = false
</script>

<div data-theme="wa" class="bg-white">
  <div class="h-screen flex flex-col">
    <Router {routes} />
  </div>
</div>
