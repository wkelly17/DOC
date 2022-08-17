<script lang="ts">
  import LoadingIndicator from './LoadingIndicator.svelte'
  // @ts-ignore
  import Autocomplete from 'simple-svelte-autocomplete'
  import { push } from 'svelte-spa-router'
  import { lang0NameAndCode, lang1NameAndCode } from '../stores/LanguagesStore'

  const API_ROOT_URL: string = <string>import.meta.env.VITE_BACKEND_API_URL
  const LANGUAGE_CODES_AND_NAMES: string = '/language_codes_and_names'

  async function getLangCodesAndNames(): Promise<Array<string>> {
    const response = await fetch(API_ROOT_URL + LANGUAGE_CODES_AND_NAMES)
    const langCodesAndNames: Array<string> = await response.json()
    if (!response.ok) {
      console.log(`Error: ${response.statusText}`)
      throw new Error(response.statusText)
    }
    return langCodesAndNames
  }

  // Resolve promise for data
  let langCodesAndNames: Array<string>
  $: {
    getLangCodesAndNames()
      .then(langCodesAndNames_ => {
        langCodesAndNames = langCodesAndNames_
      })
      .catch(err => console.log(err)) // FIXME Trigger dialog or ? for error
  }

  let showAnotherLang = false
  function handleAddLang() {
    showAnotherLang = true
  }

  function resetLanguages() {
    $lang0NameAndCode = ''
    $lang1NameAndCode = ''
    showAnotherLang = false
  }

  function submitLanguages() {
    push('#/')
  }
</script>

<div class="bg-white flex">
  <button
    class="bg-white hover:bg-grey-100 text-grey-darkest font-bold py-2 px-4 rounded inline-flex items-center"
    on:click={() => push('#/')}
  >
    <svg
      width="16"
      height="16"
      viewBox="0 0 16 16"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        d="M15.9999 7.00002V9.00002H3.99991L9.49991 14.5L8.07991 15.92L0.159912 8.00002L8.07991 0.0800171L9.49991 1.50002L3.99991 7.00002H15.9999Z"
        fill="#1A130B"
      />
    </svg>
    <span class="ml-2">Languages</span>
  </button>
</div>
<div class="mx-auto w-full px-2 pt-2 mt-2">
  <h3>{import.meta.env.VITE_LANG_0_HEADER}</h3>
  {#if !langCodesAndNames}
    <LoadingIndicator />
  {:else}
    <Autocomplete items={langCodesAndNames} bind:selectedItem={$lang0NameAndCode} />
  {/if}
</div>

{#if $lang0NameAndCode && !$lang1NameAndCode && !showAnotherLang}
  <div class="mx-auto w-full px-2 pt-2 mt-2">
    <button on:click|preventDefault={handleAddLang} class="btn"
      >{import.meta.env.VITE_ADD_ANOTHER_LANGUAGE_BUTTON_TXT}</button
    >
  </div>
{/if}

{#if $lang1NameAndCode || showAnotherLang}
  <div class="mx-auto w-full px-2 pt-2 mt-2">
    <h3>{import.meta.env.VITE_LANG_1_HEADER}</h3>
    {#if !langCodesAndNames}
      <LoadingIndicator />
    {:else}
      <Autocomplete items={langCodesAndNames} bind:selectedItem={$lang1NameAndCode} />
    {/if}
  </div>
{/if}

{#if $lang0NameAndCode}
  <div class="mx-auto w-full px-2 pt-2 mt-2">
    <button on:click|preventDefault={submitLanguages} class="btn"
      >Add ({#if $lang1NameAndCode}{2}{:else}{1}{/if}) Languages</button
    >
  </div>

  <div class="mx-auto w-full px-2 pt-2 mt-2">
    <button on:click|preventDefault={resetLanguages} class="btn">Reset languages</button>
  </div>
{/if}
