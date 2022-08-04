<script lang="ts">
  import LoadingIndicator from './LoadingIndicator.svelte'
  // @ts-ignore
  import Autocomplete from 'simple-svelte-autocomplete'
  import { push } from 'svelte-spa-router'
  import { lang0NameAndCode, lang1NameAndCode } from '../stores/LanguagesStore'

  export const API_ROOT_URL: string = <string>import.meta.env.VITE_BACKEND_API_URL
  const LANGUAGE_CODES_AND_NAMES: string = '/language_codes_and_names'

  async function getLang0CodesAndNames(): Promise<string[]> {
    const response = await fetch(API_ROOT_URL + LANGUAGE_CODES_AND_NAMES)
    const json = await response.json()
    if (response.ok) {
      return <string[]>json
    } else {
      throw new Error(json)
    }
  }

  let showAnotherLang = false
  function handleAddLang() {
    showAnotherLang = true
  }

  async function getLang1CodesAndNames(): Promise<string[]> {
    const response = await fetch(API_ROOT_URL + LANGUAGE_CODES_AND_NAMES)
    const json = await response.json()
    if (response.ok) {
      return <string[]>json
    } else {
      throw new Error(json)
    }
  }

  function resetLanguages() {
    $lang0NameAndCode = ''
    $lang1NameAndCode = ''
    showAnotherLang = false
  }

  // Get the part of the lang name and code store that we want to show
  // reactively.
  $: lang0Name = $lang0NameAndCode.toString().split(',')[1]?.split('(')[0]
  $: lang1Name = $lang1NameAndCode.toString().split(',')[1]?.split('(')[0]
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
  {#await getLang0CodesAndNames()}
    <LoadingIndicator />
  {:then data}
    <Autocomplete items={data} bind:selectedItem={$lang0NameAndCode} />
  {:catch error}
    <p class="error">{error.message}</p>
  {/await}
</div>

{#if $lang0NameAndCode && !$lang1NameAndCode && !showAnotherLang}
  <div class="mx-auto w-full px-2 pt-2 mt-2">
    <button on:click|preventDefault={handleAddLang} class="btn"
      >{import.meta.env.VITE_ADD_ANOTHER_LANGUAGE_BUTTON_TXT}</button
    >
  </div>
{/if}

{#if showAnotherLang}
  <div class="mx-auto w-full px-2 pt-2 mt-2">
    <h3>{import.meta.env.VITE_LANG_1_HEADER}</h3>
    {#await getLang1CodesAndNames()}
      <LoadingIndicator />
    {:then data}
      <Autocomplete items={data} bind:selectedItem={$lang1NameAndCode} />
    {:catch error}
      <p class="error">{error.message}</p>
    {/await}
  </div>
{/if}

{#if $lang0NameAndCode}
  <div class="toast toast-top toast-center">
    <div class="alert alert-success shadow-lg elementToFadeInAndOut">
      <div>
        <span class="capitalize">{lang0Name}</span> successfully stored
      </div>
    </div>
    {#if $lang1NameAndCode}
      <div class="alert alert-success shadow-lg elementToFadeInAndOut">
        <div>
          <span class="capitalize">{lang1Name}</span> successfully stored
        </div>
      </div>
    {/if}
  </div>
{/if}

<!-- {#if !isEmpty($lang0NameAndCode)} -->
<!--   <div class="mx-auto w-full px-2 pt-2 mt-2"> -->
<!--     <button on:click|preventDefault={submitLanguage} class="btn" -->
<!--       >Add ({#if !isEmpty($lang1NameAndCode)}{2}{:else}{1}{/if}) Languages</button -->
<!--     > -->
<!--   </div> -->

{#if $lang0NameAndCode}
  <div class="mx-auto w-full px-2 pt-2 mt-2">
    <button on:click|preventDefault={resetLanguages} class="btn">Reset languages</button>
  </div>
{/if}

<style>
  .elementToFadeInAndOut {
    -webkit-animation: fadeinout 8s linear 1 forwards;
    animation: fadeinout 8s linear 1 forwards;
  }

  @-webkit-keyframes fadeinout {
    0% {
      opacity: 0;
    }
    50% {
      opacity: 1;
    }
    100% {
      opacity: 0;
    }
  }
  @keyframes fadeinout {
    0% {
      opacity: 0;
    }
    50% {
      opacity: 1;
    }
    100% {
      opacity: 0;
    }
  }
</style>
