<script lang="ts">
  import Mast from './Mast.svelte'
  import Tabs from './Tabs.svelte'
  import Sidebar from './Sidebar.svelte'
  import { setShowTopMatter } from '../lib/utils'

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
          This document generator allows you to interleave different types of resources
          from different languages into a single document. You can find a more basic
          (limited) version of this app
          <span style="text-decoration-line: underline"> <a href="#/">here</a></span
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
        <!-- svelte-ignore security-anchor-rel-noreferrer -->
        <a
          href="https://creativecommons.org/licenses/by-sa/4.0/"
          target="_blank"
          class="link"
        >
          CCBYSA 4.0 ShareAlike license </a
        >.
      </span>
    </div>
  </li>
  <li class="bg-white p-2">
    <span class="text-secondary-content text-lg">Version Information</span>
    <div>
      <span class="text-neutral-content">
        <p>Build date: {import.meta.env.VITE_DOC_BUILD_TIMESTAMP}</p>
        <!-- svelte-ignore security-anchor-rel-noreferrer -->
        <p>
          Git Hash:
          <a
            href="https://github.com/WycliffeAssociates/DOC/commits/{import.meta.env.VITE_DOC_VERSION}"
            target="_blank"
            class="link"
          >
            {import.meta.env.VITE_DOC_VERSION}
          </a>
        </p>
      </span>
    </div>
  </li>
</ul>
