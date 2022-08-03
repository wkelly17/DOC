<script lang="ts">
  import { lang0NameAndCode, lang1NameAndCode } from '../stores/LanguagesStore'

  // Get the part of the language name and code store that we want to show
  // reactively, i.e., the language name.
  $: lang0Name = $lang0NameAndCode.toString().split(',')[1]?.split('(')[0]
  $: lang1Name = $lang1NameAndCode.toString().split(',')[1]?.split('(')[0]
</script>

<ul>
  <li class="bg-white border-b-4 border-orange-500 p-2">
    <span class="text-xl text-orange-600"><a href="#/languages">Languages</a></span>
    {#if $lang0NameAndCode}
      <div>
        <span class="text-grey-200 text-sm capitalize"
          >{lang0Name}{#if $lang1NameAndCode},
            {lang1Name}{/if}</span
        >
      </div>
    {/if}
  </li>
  <li><a href="#/resource_types">Resource types</a></li>
  <li><a href="#/books">Books</a></li>
</ul>
