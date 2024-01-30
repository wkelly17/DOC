<script lang="ts">
  import { settingsUpdated } from '$lib/stores/SettingsStore'
  export let id = ''
  export let checked = false
  export let disabled = false
</script>

<label for={id}>
  <div class="switch">
    <input
      {id}
      name={id}
      type="checkbox"
      class="sr-only"
      {disabled}
      bind:checked
      on:change={() => ($settingsUpdated = true)}
    />
    <div class="track" />
    <div class="thumb" />
  </div>
</label>

<style global lang="postcss">
  .switch {
    @apply relative inline-block align-middle cursor-pointer select-none bg-transparent;
  }
  .track {
    @apply w-11 h-7 bg-white border border-[#343434] rounded-full shadow-inner;
  }
  .thumb {
    @apply transition-all duration-300 ease-in-out absolute top-1 left-1 w-5 h-5 bg-[#343434] rounded-full;
  }
  input[type='checkbox']:checked ~ .thumb {
    @apply transform translate-x-4;
  }
  input[type='checkbox']:checked ~ .track {
    @apply transform transition-colors;
    background: linear-gradient(180deg, #1876fd 0%, #015ad9 100%),
                linear-gradient(0deg, #343434, #343434);
  }
  input[type='checkbox']:disabled ~ .track {
    @apply bg-gray-500;
  }
  input[type='checkbox']:disabled ~ .thumb {
    @apply bg-gray-100 border-gray-500;
  }
  input[type='checkbox']:focus + .track,
  input[type='checkbox']:active + .track {
    @apply outline outline-2;
  }
</style>
