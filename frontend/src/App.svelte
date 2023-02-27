<script lang="ts">
  import Router from 'svelte-spa-router'
  import routes from './routes.js'
  import 'fluent-svelte/theme.css' // Required for ProgressRing component
  let open = false
</script>

<main data-theme="wa" class="bg-white">
  <div class="container mx-auto w-full lg:w-3/5 px-2 pt-2 mt-2">
    <Router {routes} />
  </div>
</main>
