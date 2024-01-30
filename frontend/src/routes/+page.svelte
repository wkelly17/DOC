<script lang="ts">
  import { redirect } from '@sveltejs/kit'

  export function load(): void {
    throw redirect(307, '/languages')
  }
</script>
