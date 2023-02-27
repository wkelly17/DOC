<script lang="ts">
  import Logo from './Logo_v1.svelte'
  import { uiLanguages, selectedUiLanguageStore } from '../../stores/v1_release/UiSettingsStore_v1'
  import { printToConsole } from '../../lib/v1_release/utils_v1'

  export let open = false

  function handleLanguageChange(event: Event) {
    printToConsole('Changed UI display language')
  }
</script>

<aside
  tabindex="-1"
  class="fixed w-full h-full bg-secondary border-r-2 shadow-lg"
  class:open
>
  <div class="flex justify-start pl-16 pt-8">
    <Logo />
  </div>
  <nav tabindex="-1" class="pl-20 p-12 text-xl">
    <a tabindex="-1" class="block" href="">Processes</a>
    <a tabindex="-1" class="block" href="">Tools</a>
    <a tabindex="-1" class="block" href="">Resources</a>
    <a tabindex="-1" class="block" href="">Support</a>

    <div class="flex justify-between pt-4">
      <select
        bind:value={$selectedUiLanguageStore}
        on:change={event => handleLanguageChange(event)}
        class="bg-secondary"
      >
        {#each uiLanguages as language}
          <option value={language}
            ><span class="text-primary-content text-white bg-secondary">{language}</span
            ></option
          >
        {/each}
      </select>
    </div>
  </nav>
</aside>

<style>
  aside {
    right: -100%;
    transition: right 0.3s ease-in-out;
    z-index: 30;
  }

  .open {
    right: 0;
  }
</style>
