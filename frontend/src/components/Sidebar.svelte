<script>
  export let open = false
</script>

<aside class="absolute w-full h-full bg-secondary border-r-2 shadow-lg" class:open>
  <nav class="p-12 text-xl">
    <a class="block" href="">Processes</a>
    <a class="block" href="">Tools</a>
    <a class="block" href="">Resources</a>
    <a class="block" href="">Support</a>
  </nav>
</aside>

<style>
  aside {
    right: -100%;
    transition: right 0.3s ease-in-out;
  }

  .open {
    right: 0;
  }
</style>
