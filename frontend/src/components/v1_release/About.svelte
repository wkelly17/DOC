<script lang="ts">
  import Mast from './Mast.svelte'
  import Tabs from './Tabs.svelte'
  import Sidebar from './Sidebar.svelte'
  import { setShowTopMatter } from '../../lib/v1_release/utils'

  // For sidebar
  let open = false
  let showTopMatter: boolean = setShowTopMatter()
</script>

{#if showTopMatter}
<Sidebar bind:open />
<Mast bind:sidebar="{open}" />
<Tabs />
{/if}

<ul>
  <li class="bg-white p-2">
    <span class="text-secondary-content text-lg">About this tool</span>
    <div>
      <span class="text-neutral-content"
        ><p>
          This basic version of the document generator allows you to generate documents
          containing scripture and translation notes only for gateway languages only.
          There is a full version of this system available
          <span style="text-decoration-line: underline">
            <a href="#/experimental">here</a></span
          >.
        </p>
        <p>Larger documents will take more time to generate.</p></span
      >
    </div>
  </li>

  <li class="bg-white p-2">
    <span class="text-secondary-content text-lg">Tech Support</span>
    <div>
      <span class="text-neutral-content">
        Please send all questions or concerns to helpdesk@wycliffeassociates.org.
      </span>
    </div>
  </li>
  <li class="bg-white p-2">
    <span class="text-secondary-content text-lg">Licensing</span>
    <div>
      <span class="text-neutral-content">
        Unless otherwise noted, all content on this site is licensed under a
        <a
          href="https://creativecommons.org/licenses/by-sa/4.0/"
          target="_blank"
          class="link"
          >CCBYSA 4.0 ShareAlike license</a
        >.
      </span>
    </div>
  </li>
</ul>
