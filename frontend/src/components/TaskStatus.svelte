<script lang="ts">
  import ProgressIndicator from './ProgressIndicator.svelte'
  import { taskStateStore } from '../stores/TaskStore'
</script>

<div class="flex">
  {#if $taskStateStore === "Locating assets"}
  <div class="h-1 w-1/2 bg-[#F2F3F5]">
    <div class="h-1 blue-gradient-bar" style="width: 5%"></div>
  </div>
  {:else if $taskStateStore === "Provisioning asset files"}
  <div class="h-1 w-1/2 bg-[#F2F3F5]">
    <div class="h-1 blue-gradient-bar" style="width: 10%"></div>
  </div>
  {:else if $taskStateStore === "Parsing asset files"}
  <div class="h-1 w-1/2 bg-[#F2F3F5]">
    <div class="h-1 blue-gradient-bar" style="width: 20%"></div>
  </div>
  {:else if $taskStateStore === "Assembling content"}
  <div class="h-1 w-1/2 bg-[#F2F3F5]">
    <div class="h-1 blue-gradient-bar" style="width: 50%"></div>
  </div>
  {:else if $taskStateStore === "Provisioning USFM asset files for TW resource"}
  <div class="h-1 w-1/2 bg-[#F2F3F5]">
    <div class="h-1 blue-gradient-bar" style="width: 55%"></div>
  </div>
  {:else if $taskStateStore === "Parsing USFM asset files for TW resource"}
  <div class="h-1 w-1/2 bg-[#F2F3F5]">
    <div class="h-1 blue-gradient-bar" style="width: 60%"></div>
  </div>
  {:else if $taskStateStore === "Limiting TW words"}
  <div class="h-1 w-1/2 bg-[#F2F3F5]">
    <div class="h-1 blue-gradient-bar" style="width: 65%"></div>
  </div>
  {:else if $taskStateStore === "Converting to PDF" || $taskStateStore === "Converting to ePub" || $taskStateStore === "Converting to Docx"}
  <div class="h-1 w-1/2 bg-[#F2F3F5]">
    <div class="h-1 blue-gradient-bar" style="width: 70%"></div>
  </div>
  {:else}
  <div class="h-1 w-1/2 bg-[#F2F3F5]">
    <div class="h-1 blue-gradient-bar" style="width: 0%"></div>
  </div>
  {/if}
</div>
{#if $taskStateStore}
<p id="state" class="text-[#B3B9C2]">
  <ProgressIndicator labelString="{$taskStateStore}" />
</p>
{/if}

<style>
  * :global(.blue-gradient-bar) {
    background: linear-gradient(180deg, #1876fd 0%, #015ad9 100%);
  }
</style>
