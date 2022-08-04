<script lang="ts">
  import { lang0NameAndCode, lang1NameAndCode } from '../stores/LanguagesStore'
  import { push } from 'svelte-spa-router'

  // Get the part of the language name and code store that we want to show
  // reactively, i.e., the language name.
  $: lang0Name = $lang0NameAndCode.toString().split(',')[0]
  $: lang1Name = $lang1NameAndCode.toString().split(',')[0]
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
    <!-- {#if $lang0NameAndCode} -->
    <!--   <div> -->
    <!--     <span class="text-grey-200 text-sm capitalize" -->
    <!--       >{lang0Name}{#if $lang1NameAndCode}, -->
    <!--         {lang1Name}{/if}</span -->
    <!--     > -->
    <!--   </div> -->
    <!-- {/if} -->
  </li>
  <li><a href="#/resource_types">Resource types</a></li>
</ul>
