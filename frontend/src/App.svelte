<script lang="ts">
  import Router from 'svelte-spa-router'
  import routes from './routes.js'
  import Mast from './components/Mast.svelte'
  import Tabs from './components/Tabs.svelte'
  import Sidebar from './components/Sidebar.svelte'
  import 'fluent-svelte/theme.css' // Required for ProgressRing component
  let open = false
</script>

<main data-theme="wa" class="bg-white">
  <Sidebar bind:open />
  <Mast bind:sidebar={open} />
  <Tabs />
  <div class="container mx-auto w-full lg:w-3/5 px-2 pt-2 mt-2">
    <Router {routes} />
  </div>
</main>
