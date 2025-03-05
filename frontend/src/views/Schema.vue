<template>
  <div class="schema">
    <h1>Database Schema</h1>
    <div class="schema-container">
      <div v-html="renderedDiagram" class="mermaid-output"></div>
    </div>
  </div>
</template>

<script>
import { onMounted, ref } from 'vue'

export default {
  name: 'Schema',
  setup() {
    const renderedDiagram = ref('')

    const diagramDefinition = `
      <pre class="mermaid">
      erDiagram
        TestSuite ||--o{ TestCase : "has"
        TestCase ||--o{ TestCaseResult : "has"
        TestRun ||--o{ TestCaseResult : "has"
        TestOperator ||--o{ TestRun : "performs"
        Company ||--o{ TestOperator : "employs"
        TestRunTemplate }o--o{ TestCase : "includes"
        DUT }o--o{ Capability : "has"
        Specification ||--o{ Requirement : "defines"
        
        TestSuite {
          string id PK
          string name
          string url
          string format
          int version
          string version_string
          boolean is_final
        }
        
        TestCase {
          int id PK
          string id_str
          string title
          int version
          string version_string
          string test_suite_id FK
          string applies_to
          string description
          string steps
          string precondition
          string area
          string automatability
          string author
          string material
          boolean is_challenged
          string challenge_issue_url
        }
        
        TestRun {
          int id PK
          string status
          int operator_id FK
        }
        
        TestCaseResult {
          int id PK
          string result
          string logs
          string comment
          string artifacts
          int test_case_id FK
          int test_run_id FK
        }
        
        TestOperator {
          int id PK
          string name
          string mail
          string login
          string access_rights
          int company_id FK
        }
        
        Company {
          int id PK
          string name
          string access_rights
        }
        
        TestRunTemplate {
          int id PK
          string id_str
          string name
          string description
          string field
        }
        
        DUT {
          int id PK
          string product_name
          string make
          string model
          string countries
          string parent
        }
        
        Capability {
          int id PK
          string name
          string category
          int version
          string version_string
        }
        
        Specification {
          int id PK
          string name
          string url
          string version
        }
        
        Requirement {
          int id PK
          string field
          int specification_id FK
        }
      </pre>
    `

    onMounted(async () => {
      // Use CDN version of mermaid instead of importing it
      if (!document.getElementById('mermaid-script')) {
        const script = document.createElement('script')
        script.id = 'mermaid-script'
        script.src = 'https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js'
        script.onload = () => {
          window.mermaid.initialize({
            startOnLoad: true,
            theme: 'default',
            securityLevel: 'loose',
            er: {
              diagramPadding: 20
            }
          })
          renderedDiagram.value = diagramDefinition
          setTimeout(() => {
            window.mermaid.init(undefined, document.querySelectorAll('.mermaid'))
          }, 200)
        }
        document.head.appendChild(script)
      } else {
        renderedDiagram.value = diagramDefinition
        setTimeout(() => {
          window.mermaid.init(undefined, document.querySelectorAll('.mermaid'))
        }, 200)
      }
    })

    return {
      renderedDiagram
    }
  }
}
</script>

<style scoped>
.schema {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem;
}

.schema-container {
  background-color: white;
  border-radius: 8px;
  padding: 2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: auto;
}

.mermaid-output {
  font-family: 'Trebuchet MS', 'Lucida Sans Unicode', 'Lucida Grande', 'Lucida Sans', Arial, sans-serif;
}

h1 {
  margin-bottom: 2rem;
}

/* Override scoped styles for mermaid elements */
:deep(.mermaid) {
  overflow: visible;
}

:deep(svg) {
  max-width: 100%;
}
</style>
