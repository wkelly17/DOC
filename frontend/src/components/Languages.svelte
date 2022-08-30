<script lang="ts">
  import ProgressIndicator from './ProgressIndicator.svelte'
  import LeftArrow from './LeftArrow.svelte'
  import { push } from 'svelte-spa-router'
  import {
    lang0NameAndCodeStore,
    lang1NameAndCodeStore,
    lang0CodeStore,
    lang1CodeStore,
    lang0NameStore,
    lang1NameStore,
    langCodeAndNamesStore,
    langCountStore
  } from '../stores/LanguagesStore'
  import { resetStores } from '../lib/utils'

  const apiRootUrl: string = <string>import.meta.env.VITE_BACKEND_API_URL
  const langCodesAndNamesUrl: string = <string>import.meta.env.VITE_LANG_CODES_NAMES_URL

  async function getLangCodesNames(): Promise<Array<string>> {
    const response = await fetch(`${apiRootUrl}${langCodesAndNamesUrl}`)
    const langCodesAndNames: Array<string> = await response.json()
    if (!response.ok) {
      console.log(`Error: ${response.statusText}`)
      throw new Error(response.statusText)
    }
    return langCodesAndNames
  }

  // Resolve promise for data
  let langCodesAndNames: Array<string> = []
  $: {
    getLangCodesNames()
      .then(langCodesAndNames_ => {
        langCodesAndNames = langCodesAndNames_
      })
      .catch(err => console.log(err)) // FIXME Trigger toast for error
  }

  const maxLanguages = 2

  function resetLanguages() {
    resetStores('languages')
  }

  function submitLanguages() {
    push('#/')
  }

  // Update the langCountStore reactively
  $: {
    if ($langCodeAndNamesStore.length > 0) {
      langCountStore.set($langCodeAndNamesStore.length)
    } else {
      langCountStore.set(0)
    }
  }

  // Filter the language list reactively
  let langSearchTerm: string = ''
  let filteredlangCodeAndNames: Array<string> = []
  $: {
    if (langCodesAndNames) {
      filteredlangCodeAndNames = langCodesAndNames.filter(item =>
        item.toLowerCase().split(', code:')[0].includes(langSearchTerm.toLowerCase())
      )
    }
  }

  // Update stores for use in this and other pages reactively
  $: lang0CodeStore.set($langCodeAndNamesStore[0]?.split(', code: ')[1])
  $: lang1CodeStore.set($langCodeAndNamesStore[1]?.split(', code: ')[1])
  $: lang0NameStore.set($langCodeAndNamesStore[0]?.split(', code: ')[0])
  $: lang1NameStore.set($langCodeAndNamesStore[1]?.split(', code: ')[0])
</script>

<div class="bg-primary">
  <div class="bg-primary flex">
    <button
      class="bg-primary hover:bg-grey-100 py-2 px-4 rounded inline-flex items-center"
      on:click={() => push('#/')}
    >
      <LeftArrow backLabel="Languages" />
    </button>
  </div>
  <div class="mx-auto w-full px-2 pt-2 mt-2">
    {#if !langCodesAndNames}
      <ProgressIndicator />
    {:else}
      <label id="label-for-filter-langs" for="filter-langs">
        <input
          id="filter-langs"
          bind:value={langSearchTerm}
          placeholder="Filter languages"
          class="input input-bordered bg-primary w-full max-w-xs mb-4"
        />
      </label>
      <p class="text-neutral-content mb-4">
        Please select up to 2 languages you want to add.
      </p>
    {/if}
  </div>

  <ul>
    {#each langCodesAndNames as langCodeAndName, index}
      <li
        style={filteredlangCodeAndNames.includes(langCodeAndName) ? '' : 'display :none'}
      >
        <label for="lang-code-{index}" class="text-secondary-content"
          >{langCodeAndName.split(', code: ')[0]}</label
        >
        <input
          id="lang-code-{index}"
          type="checkbox"
          bind:group={$langCodeAndNamesStore}
          value={langCodeAndName}
          class="checkbox"
        />
      </li>
    {/each}
  </ul>
  {#if $langCountStore > 0 && $langCountStore <= maxLanguages}
    <div class="mx-auto  px-2 pt-2 mt-2 mb-4">
      <button
        on:click|preventDefault={submitLanguages}
        class="btn orange-gradient w-5/6 capitalize"
        >Add ({$langCountStore}) Languages</button
      >
    </div>
    <div class="mx-auto w-full px-2 pt-2 mb-8">
      <button
        class="btn gray-gradiant text-neutral-content w-5/6 rounded capitalize"
        on:click|preventDefault={() => resetLanguages()}>Reset languages</button
      >
    </div>
  {/if}
  {#if $langCountStore > maxLanguages}
    <div class="toast toast-center toast-middle">
      <div class="alert alert-error">
        <div>
          <span
            >You've selected more than two languages, please choose up to two languages.</span
          >
        </div>
      </div>
    </div>
  {/if}
</div>

<style global lang="postcss">
  @tailwind base;
  @tailwind components;
  @tailwind utilities;
  * :global(label[id='label-for-filter-langs']) {
    position: relative;
  }

  * :global(label[id='label-for-filter-langs']:before) {
    content: '';
    position: absolute;
    right: 10px;
    top: 0;
    bottom: 0;
    width: 20px;
    background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='25' height='25' viewBox='0 0 25 25' fill-rule='evenodd'%3E%3Cpath d='M16.036 18.455l2.404-2.405 5.586 5.587-2.404 2.404zM8.5 2C12.1 2 15 4.9 15 8.5S12.1 15 8.5 15 2 12.1 2 8.5 4.9 2 8.5 2zm0-2C3.8 0 0 3.8 0 8.5S3.8 17 8.5 17 17 13.2 17 8.5 13.2 0 8.5 0zM15 16a1 1 0 1 1 2 0 1 1 0 1 1-2 0'%3E%3C/path%3E%3C/svg%3E")
      center / contain no-repeat;
  }

  * :global(input[id='filter-langs']) {
    padding: 10px 30px;
  }

  * :global(.orange-gradient) {
    background: linear-gradient(180deg, #fdd231 0%, #fdad29 100%),
      linear-gradient(0deg, rgba(20, 14, 8, 0.6), rgba(20, 14, 8, 0.6));
  }
</style>
