<script>
  export let open = false
</script>

<button
  tabindex="-1"
  class="flex items-center btn-sm text-white hover:text-gray-100 cursor-pointer mr-2 focus:outline-none border-2 rounded"
  class:open
  on:click={() => (open = !open)}
>
  <svg width="18" height="14">
    <line id="top" x1="0" y1="2" x2="18" y2="2" />
    <line id="middle" x1="0" y1="7" x2="18" y2="7" />
    <line id="bottom" x1="0" y1="12" x2="18" y2="12" />
  </svg>
  <span class="pl-2 capitalize" class:open
    >{#if open}Close{:else}Menu{/if}</span
  >
</button>

<style>
  button {
    border-color: #ffffff4d;
  }

  svg {
    min-height: 14px;
    transition: transform 0.3s ease-in-out;
  }

  svg line {
    stroke: currentColor;
    stroke-width: 3;
    transition: transform 0.3s ease-in-out;
  }

  button {
    z-index: 30;
  }

  /* .open svg { */
  /*   transform: scale(1.2); */
  /* } */

  .open #top {
    transform: translate(3px, 0px) rotate(45deg);
  }

  .open #middle {
    opacity: 0;
  }

  .open #bottom {
    transform: translate(-6px, 6px) rotate(-45deg);
  }
</style>
