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

  // FIXME Using .env value here always yields undefinhed
  // const numBooksToShow = <number>import.meta.env.NUM_BOOKS_TO_SHOW
  const numBooksToShow = 5
  $: console.log(`numBooksToShow: ${numBooksToShow}`)
  $: otBooksAbbr = otBooks.slice(0, numBooksToShow)
  $: ntBooksAbbr = ntBooks.slice(0, numBooksToShow)

  $: lang0ResourceTypeNames = $lang0ResourceTypesStore.map(
    resourceTypeAndNAme => resourceTypeAndNAme[1]
  )
  $: lang1ResourceTypeNames = $lang1ResourceTypesStore.map(
    resourceTypeAndNAme => resourceTypeAndNAme[1]
  )

  // FIXME Using .env value here always yields undefinhed
  // const numResourceTypesToShow = <number>import.meta.env.NUM_RESOURCE_TYPES_TO_SHOW
  const numResourceTypesToShow = 3
  $: console.log(`numResourceTypesToShow: ${numResourceTypesToShow}`)
  $: lang0ResourceTypeNamesAbbr = lang0ResourceTypeNames.slice(0, numResourceTypesToShow)
  // $: lang1ResourceTypeNamesAbbr = lang1ResourceTypeNames.slice(
  //   0,
  //   numResourceTypesToShow
  // )

  // Keep track of how many books are currently stored reactively.
  let nonEmptyOtBooks: boolean
  $: nonEmptyOtBooks = $otBookStore.every(item => item.length > 0)

  let nonEmptyNtBooks: boolean
  $: nonEmptyNtBooks = $ntBookStore.every(item => item.length > 0)

  let bookCount: number
  $: {
    if (nonEmptyOtBooks && nonEmptyNtBooks) {
      bookCount = $otBookStore.length + $ntBookStore.length
    } else if (nonEmptyOtBooks && !nonEmptyNtBooks) {
      bookCount = $otBookStore.length
    } else if (!nonEmptyOtBooks && nonEmptyNtBooks) {
      bookCount = $ntBookStore.length
    } else {
      bookCount = 0
    }
  }

  // Keep track of how many resources are currently stored reactively.
  let nonEmptyLang0Resourcetypes: boolean
  $: nonEmptyLang0Resourcetypes = $lang0ResourceTypesStore.every(item => item.length > 0)

  let nonEmptyLang1Resourcetypes: boolean
  $: nonEmptyLang1Resourcetypes = $lang1ResourceTypesStore.every(item => item.length > 0)

  let resourceTypesCount: number
  $: {
    if (nonEmptyLang0Resourcetypes && nonEmptyLang1Resourcetypes) {
      resourceTypesCount =
        $lang0ResourceTypesStore.length + $lang1ResourceTypesStore.length
    } else if (nonEmptyLang0Resourcetypes && !nonEmptyLang1Resourcetypes) {
      resourceTypesCount = $lang0ResourceTypesStore.length
    } else if (!nonEmptyLang0Resourcetypes && nonEmptyLang1Resourcetypes) {
      resourceTypesCount = $lang1ResourceTypesStore.length
    } else {
      resourceTypesCount = 0
    }
  }
</script>

<ul>
  <li class="bg-white border-b-4 border-grey-500 p-2">
    <button
      class="inline-flex items-center w-full justify-between text-xl text-orange-500 font-bold py-2 px-4 rounded"
      on:click={() => push('#/languages')}
    >
      <div class="flex items-center">
        <svg
          width="20"
          height="20"
          viewBox="0 0 20 20"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M14.36 12C14.44 11.34 14.5 10.68 14.5 10C14.5 9.32 14.44 8.66 14.36 8H17.74C17.9 8.64 18 9.31 18 10C18 10.69 17.9 11.36 17.74 12H14.36ZM12.59 17.56C13.19 16.45 13.65 15.25 13.97 14H16.92C15.9512 15.6683 14.4141 16.932 12.59 17.56ZM12.34 12H7.66C7.56 11.34 7.5 10.68 7.5 10C7.5 9.32 7.56 8.65 7.66 8H12.34C12.43 8.65 12.5 9.32 12.5 10C12.5 10.68 12.43 11.34 12.34 12ZM10 17.96C9.17 16.76 8.5 15.43 8.09 14H11.91C11.5 15.43 10.83 16.76 10 17.96ZM6 6H3.08C4.03886 4.32721 5.5748 3.06149 7.4 2.44C6.8 3.55 6.35 4.75 6 6ZM3.08 14H6C6.35 15.25 6.8 16.45 7.4 17.56C5.57862 16.9317 4.04485 15.6677 3.08 14ZM2.26 12C2.1 11.36 2 10.69 2 10C2 9.31 2.1 8.64 2.26 8H5.64C5.56 8.66 5.5 9.32 5.5 10C5.5 10.68 5.56 11.34 5.64 12H2.26ZM10 2.03C10.83 3.23 11.5 4.57 11.91 6H8.09C8.5 4.57 9.17 3.23 10 2.03ZM16.92 6H13.97C13.657 4.76146 13.1936 3.5659 12.59 2.44C14.43 3.07 15.96 4.34 16.92 6ZM10 0C4.47 0 0 4.5 0 10C0 12.6522 1.05357 15.1957 2.92893 17.0711C3.85752 17.9997 4.95991 18.7362 6.17317 19.2388C7.38642 19.7413 8.68678 20 10 20C12.6522 20 15.1957 18.9464 17.0711 17.0711C18.9464 15.1957 20 12.6522 20 10C20 8.68678 19.7413 7.38642 19.2388 6.17317C18.7362 4.95991 17.9997 3.85752 17.0711 2.92893C16.1425 2.00035 15.0401 1.26375 13.8268 0.761205C12.6136 0.258658 11.3132 0 10 0Z"
            fill="#140E08"
            fill-opacity="0.6"
          />
        </svg>
        <span class="ml-4">1. Languages</span>
      </div>
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
        <span class="text-grey-200 text-sm ml-14 capitalize"
          >{lang0Name}{#if $lang1NameAndCode},
            {lang1Name}{/if}</span
        >
      </div>
    {:else}
      <div>
        <span class="text-grey-200 text-sm ml-14">Select languages</span>
      </div>
    {/if}
  </li>
  <li class="bg-white border-b-4 border-grey-500 p-2">
    <button
      class="inline-flex items-center w-full justify-between text-xl text-orange-500 font-bold py-2 px-4 rounded"
      on:click={() => push('#/books')}
    >
      <div class="flex items-center">
        <svg
          width="16"
          height="20"
          viewBox="0 0 16 20"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M14 20C14.5304 20 15.0391 19.7893 15.4142 19.4142C15.7893 19.0391 16 18.5304 16 18V2C16 1.46957 15.7893 0.960859 15.4142 0.585786C15.0391 0.210714 14.5304 0 14 0H8V7L5.5 5.5L3 7V0H2C1.46957 0 0.960859 0.210714 0.585786 0.585786C0.210714 0.960859 0 1.46957 0 2V18C0 18.5304 0.210714 19.0391 0.585786 19.4142C0.960859 19.7893 1.46957 20 2 20H14Z"
            fill="#140E08"
          />
        </svg>
        <span class="ml-4">2. Books</span>
      </div>
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
    {#if bookCount > 0}
      <div>
        <span class="text-grey-200 text-sm ml-14 capitalize"
          >{#if otBooks && otBooks.length > numBooksToShow}{otBooksAbbr}...{:else}{otBooks}{/if}{#if ntBooks && ntBooks.length > numBooksToShow},
            {ntBooksAbbr}...{:else}{ntBooks}{/if}</span
        >
      </div>
    {:else}
      <div>
        <span class="text-grey-200 text-sm ml-14">Select books</span>
      </div>
    {/if}
  </li>
  <li class="bg-white p-2">
    <button
      class="inline-flex items-center w-full justify-between text-xl text-orange-500 font-bold py-2 px-4 rounded"
      on:click={() => push('#/resource_types')}
    >
      <div class="flex items-center">
        <svg
          width="16"
          height="20"
          viewBox="0 0 16 20"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M2 0C1.46957 0 0.960859 0.210714 0.585786 0.585786C0.210714 0.960859 0 1.46957 0 2V18C0 18.5304 0.210714 19.0391 0.585786 19.4142C0.960859 19.7893 1.46957 20 2 20H14C14.5304 20 15.0391 19.7893 15.4142 19.4142C15.7893 19.0391 16 18.5304 16 18V6L10 0H2ZM2 2H9V7H14V18H2V2ZM4 10V12H12V10H4ZM4 14V16H9V14H4Z"
            fill="#140E08"
            fill-opacity="0.6"
          />
        </svg>
        <span class="ml-4">3. Resource types</span>
      </div>
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
    {#if resourceTypesCount > 0}
      <div>
        <span class="text-grey-200 text-sm ml-14 capitalize"
          >{#if lang0ResourceTypeNames && lang0ResourceTypeNames.length > numResourceTypesToShow}{lang0ResourceTypeNamesAbbr}...{:else}{lang0ResourceTypeNames}{/if}
        </span>
      </div>
    {:else}
      <div>
        <span class="text-grey-200 text-sm ml-14">Select resource types</span>
      </div>
    {/if}
  </li>
</ul>
<div class="flex items-center justify-center h-28 bg-white">
  <button
    class="flex btn  btn-disabled w-5/6 rounded"
    on:click={() => console.log('generate document...')}
  >
    <span class="text-xl py-2 px-4 text-gray-500 capitalize">Generate Document</span>
  </button>
</div>
