<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, shallowRef, watch } from 'vue'
import { useData } from 'vitepress'

const props = defineProps<{ modelValue: string; readonly?: boolean; minLines?: number }>()
const emit = defineEmits<{ (e: 'update:modelValue', v: string): void; (e: 'run'): void; (e: 'focus'): void }>()

const host = ref<HTMLElement>()
const view = shallowRef<any>()
const { isDark } = useData()
let themeComp: any
let mods: any

onMounted(async () => {
  const [cm, state, viewMod, lang, py, dark, commands] = await Promise.all([
    import('codemirror'),
    import('@codemirror/state'),
    import('@codemirror/view'),
    import('@codemirror/language'),
    import('@codemirror/lang-python'),
    import('@codemirror/theme-one-dark'),
    import('@codemirror/commands'),
  ])
  mods = { state, viewMod, lang, dark }
  themeComp = new state.Compartment()
  const lightTheme = [lang.syntaxHighlighting(lang.defaultHighlightStyle, { fallback: true })]
  const runKey = viewMod.keymap.of([
    { key: 'Mod-Enter', run: () => { emit('run'); return true } },
    { key: 'Shift-Enter', run: () => { emit('run'); return true } },
    commands.indentWithTab,
  ])
  view.value = new viewMod.EditorView({
    parent: host.value!,
    state: state.EditorState.create({
      doc: props.modelValue,
      extensions: [
        runKey,
        cm.basicSetup,
        py.python(),
        state.EditorState.tabSize.of(4),
        lang.indentUnit.of('    '),
        state.EditorState.readOnly.of(!!props.readonly),
        viewMod.EditorView.editable.of(!props.readonly),
        themeComp.of(isDark.value ? dark.oneDark : lightTheme),
        viewMod.EditorView.updateListener.of((u: any) => {
          if (u.docChanged) emit('update:modelValue', u.state.doc.toString())
          if (u.focusChanged && u.view.hasFocus) emit('focus')
        }),
        viewMod.EditorView.theme({
          '&': { fontSize: '14px', backgroundColor: 'var(--vp-code-block-bg)' },
          '.cm-content': { fontFamily: 'var(--vp-font-family-mono)', minHeight: `${(props.minLines || 3) * 1.5}em` },
          '.cm-gutters': { backgroundColor: 'var(--vp-code-block-bg)', border: 'none', color: 'var(--vp-c-text-3)' },
          '&.cm-focused': { outline: 'none' },
        }),
      ],
    }),
  })
  watch(isDark, (d) => {
    view.value?.dispatch({ effects: themeComp.reconfigure(d ? dark.oneDark : lightTheme) })
  })
})

watch(
  () => props.modelValue,
  (v) => {
    const vw = view.value
    if (vw && v !== vw.state.doc.toString()) {
      vw.dispatch({ changes: { from: 0, to: vw.state.doc.length, insert: v } })
    }
  },
)

onBeforeUnmount(() => view.value?.destroy())
</script>

<template>
  <div class="py-editor" ref="host">
    <pre v-if="!view" class="py-editor-fallback"><code>{{ modelValue }}</code></pre>
  </div>
</template>
