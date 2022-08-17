<script lang="ts">
  import { lang0NameAndCode, lang1NameAndCode } from '../stores/LanguagesStore'
  import { otBookStore, ntBookStore } from '../stores/BooksStore'
  import {
    lang0ResourceTypesStore,
    lang1ResourceTypesStore
  } from '../stores/ResourceTypesStore'
  import { push } from 'svelte-spa-router'

  // Get the language name from the store reactively.
  $: lang0Name = $lang0NameAndCode.toString().split(',')[0]
  $: lang1Name = $lang1NameAndCode.toString().split(',')[0]
  // Get the book names from the store reactively.
  $: otBooks = $otBookStore.map(resourceCodeAndName => resourceCodeAndName[1])
  $: ntBooks = $ntBookStore.map(resourceCodeAndName => resourceCodeAndName[1])

  $: lang0ResourceTypeNames = $lang0ResourceTypesStore.map(
    resourceTypeAndNAme => resourceTypeAndNAme[1]
  )
  $: lang1ResourceTypeNames = $lang1ResourceTypesStore.map(
    resourceTypeAndNAme => resourceTypeAndNAme[1]
  )
</script>

<ul>
  <li class="bg-white border-b-4 border-orange-500 p-2">
    <button
      class="inline-flex items-center w-full justify-between text-xl text-orange-500 font-bold py-2 px-4 rounded"
      on:click={() => push('#/languages')}
    >
      <span>Languages</span>
      <svg
        width="16"
        height="16"
        viewBox="0 0 16 16"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          d="M0 7.00002V9.00002H12L6.5 14.5L7.92 15.92L15.84 8.00002L7.92 0.0800171L6.5 1.50002L12 7.00002H0Z"
          fill="#140E08"
        />
      </svg>
    </button>
    {#if $lang0NameAndCode}
      <div>
        <span class="text-grey-200 text-sm capitalize"
          >{lang0Name}{#if $lang1NameAndCode},
            {lang1Name}{/if}</span
        >
      </div>
    {/if}
  </li>
  <li class="bg-white border-b-4 border-orange-500 p-2">
    <button
      class="inline-flex items-center w-full justify-between text-xl text-orange-500 font-bold py-2 px-4 rounded"
      on:click={() => push('#/books')}
    >
      <span>Books</span>
      <svg
        width="16"
        height="16"
        viewBox="0 0 16 16"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          d="M0 7.00002V9.00002H12L6.5 14.5L7.92 15.92L15.84 8.00002L7.92 0.0800171L6.5 1.50002L12 7.00002H0Z"
          fill="#140E08"
        />
      </svg>
    </button>
    {#if $otBookStore || $ntBookStore}
      <div>
        <span class="text-grey-200 text-sm capitalize"
          >{#if otBooks && otBooks.length > 5}{otBooks.slice(
              0,
              5
            )}...{:else}{otBooks}{/if}{#if ntBooks && ntBooks.length > 5}, {ntBooks.slice(
              0,
              5
            )}...{:else}{ntBooks}{/if}</span
        >
      </div>
    {/if}
  </li>
  <li class="bg-white border-b-4 border-orange-500 p-2">
    <button
      class="inline-flex items-center w-full justify-between text-xl text-orange-500 font-bold py-2 px-4 rounded"
      on:click={() => push('#/resource_types')}
    >
      <span>Resource types</span>
      <svg
        width="16"
        height="16"
        viewBox="0 0 16 16"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          d="M0 7.00002V9.00002H12L6.5 14.5L7.92 15.92L15.84 8.00002L7.92 0.0800171L6.5 1.50002L12 7.00002H0Z"
          fill="#140E08"
        />
      </svg>
    </button>
    {#if $lang0ResourceTypesStore || $lang1ResourceTypesStore}
      <div>
        <span class="text-grey-200 text-sm capitalize"
          >{#if lang0ResourceTypeNames && lang0ResourceTypeNames.length > 5}{lang0ResourceTypeNames.slice(
              0,
              5
            )}...{:else}{lang0ResourceTypeNames}{/if}{#if lang1ResourceTypeNames && lang1ResourceTypeNames.length > 5},
            {lang1ResourceTypeNames.slice(
              0,
              5
            )}...{:else}{lang1ResourceTypeNames}{/if}</span
        >
      </div>
    {/if}
  </li>
</ul>
