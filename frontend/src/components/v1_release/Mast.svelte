<script lang="ts">
  import Logo from './Logo.svelte'
  import Hamburger from './Hamburger.svelte'

  export let sidebar = false
</script>

<header class="bg-secondary flex items-center justify-between">
  <div class="flex pl-16 pt-8">
    <Logo />
  </div>
  <!-- <div class="flex pr-16 pt-8"> -->
  <!--   <div> -->
  <!--     <nav class="flex"> -->
  <!--       <Hamburger bind:open={sidebar} /> -->
  <!--     </nav> -->
  <!--   </div> -->
  <!-- </div> -->
</header>
