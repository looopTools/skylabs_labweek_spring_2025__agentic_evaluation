<template>
  <div class="test-run-templates">
    <h1>Test Run Templates</h1>
    
    <div class="actions">
      <button @click="showAddForm = !showAddForm" class="btn primary">
        {{ showAddForm ? 'Cancel' : 'Create Template' }}
      </button>
    </div>
    
    <div v-if="showAddForm" class="add-form">
      <h2>{{ isEditing ? 'Edit Template' : 'Create New Template' }}</h2>
      <form @submit.prevent="addTemplate">
        <div class="form-group">
          <label for="template_id">Template ID:</label>
          <input type="text" id="template_id" v-model="newTemplate.template_id" required>
        </div>
        
        <div class="form-group">
          <label for="name">Name:</label>
          <input type="text" id="name" v-model="newTemplate.name" required>
        </div>
        
        <div class="form-group">
          <label for="description">Description:</label>
          <textarea id="description" v-model="newTemplate.description" rows="3"></textarea>
        </div>
        
        <div class="form-group">
          <label for="field">Type:</label>
          <select id="field" v-model="newTemplate.field">
            <option value="Release">Release Test Run</option>
            <option value="Regression">Regression Test Run</option>
            <option value="Monthly">Monthly Run</option>
            <option value="Quarterly">Quarterly Run</option>
            <option value="Yearly">Yearly Run</option>
            <option value="Custom">Custom</option>
          </select>
        </div>
        
        <div class="form-group">
          <label>Select Test Cases:</label>
          <div class="test-case-selector">
            <div class="filter-controls">
              <input type="text" v-model="searchQuery" placeholder="Search test cases...">
              <select v-model="suiteFilter">
                <option value="">All Test Suites</option>
                <option v-for="suite in testSuites" :key="suite.id" :value="suite.id">
                  {{ suite.name }}
                </option>
              </select>
            </div>
            
            <div class="test-case-list">
              <div v-for="testCase in filteredTestCases" :key="testCase.id" class="test-case-item">
                <input type="checkbox" :id="`tc-${testCase.id}`" v-model="selectedTestCases" :value="testCase.id">
                <label :for="`tc-${testCase.id}`">
                  {{ testCase.title }} ({{ testCase.test_suite_id }})
                </label>
              </div>
            </div>
          </div>
        </div>
        
        <button type="submit" class="btn primary">{{ isEditing ? 'Update Template' : 'Create Template' }}</button>
      </form>
    </div>
    
    <div v-if="loading" class="loading">Loading...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="templates.length === 0" class="empty">No templates available</div>
    <div v-else class="templates-list">
      <div v-for="template in templates" :key="template.id" class="template-card">
        <div class="template-header">
          <h3>{{ template.name }}</h3>
          <span class="template-type">{{ template.field || 'Custom' }}</span>
        </div>
        
        <p v-if="template.description" class="template-description">{{ template.description }}</p>
        
        <div class="template-stats">
          <span class="test-case-count">{{ getTemplateTestCaseCount(template.id) }} Test Cases</span>
        </div>
        
        <div class="template-actions">
          <button @click="startTestRun(template.id)" class="btn primary">Start Test Run</button>
          <button @click="editTemplate(template.id)" class="btn">Edit</button>
          <button @click="deleteTemplate(template.id)" class="btn danger">Delete</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import axios from 'axios'

const API_URL = 'http://localhost:8000/api'

export default {
  name: 'TestRunTemplates',
  setup() {
    const store = useStore()
    const router = useRouter()
    const showAddForm = ref(false)
    const isEditing = ref(false)
    const searchQuery = ref('')
    const suiteFilter = ref('')
    const selectedTestCases = ref([])
    
    const newTemplate = ref({
      template_id: '',
      name: '',
      description: '',
      field: 'Custom'
    })
    
    onMounted(() => {
      store.dispatch('fetchTestRunTemplates')
      store.dispatch('fetchTestCases')
      store.dispatch('fetchTestSuites')
    })
    
    const templates = computed(() => store.state.testRunTemplates)
    const testCases = computed(() => store.state.testCases)
    const testSuites = computed(() => store.state.testSuites)
    const loading = computed(() => store.state.loading)
    const error = computed(() => store.state.error)
    
    const filteredTestCases = computed(() => {
      return testCases.value.filter(tc => {
        const matchesSearch = searchQuery.value === '' || 
          tc.title.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
          (tc.case_id && tc.case_id.toLowerCase().includes(searchQuery.value.toLowerCase()));
        
        const matchesSuite = suiteFilter.value === '' || tc.test_suite_id === suiteFilter.value;
        
        return matchesSearch && matchesSuite;
      });
    });
    
    const getTemplateTestCaseCount = (templateId) => {
      // This would need to be implemented with actual data from the backend
      return Math.floor(Math.random() * 20) + 5; // Placeholder
    };
    
    const addTemplate = async () => {
      try {
        store.commit('SET_LOADING', true)
        store.commit('SET_ERROR', null)
        
        const templateData = {
          ...newTemplate.value,
          test_cases: selectedTestCases.value
        };
        
        if (isEditing.value) {
          await axios.put(`${API_URL}/test-run-templates/${editingId.value}`, templateData)
          alert('Template updated successfully')
        } else {
          await axios.post(`${API_URL}/test-run-templates`, templateData)
          alert('Template created successfully')
        }
        
        // Reset form
        newTemplate.value = {
          template_id: '',
          name: '',
          description: '',
          field: 'Custom'
        }
        selectedTestCases.value = []
        showAddForm.value = false
        isEditing.value = false
        
        // Refresh the list
        await store.dispatch('fetchTestRunTemplates')
      } catch (error) {
        console.error('Error with template:', error)
        store.commit('SET_ERROR', (error.response && error.response.data && error.response.data.detail) || error.message || 'Failed to process template')
      } finally {
        store.commit('SET_LOADING', false)
      }
    }
    
    const editingId = ref(null)
    
    const editTemplate = (id) => {
      const template = templates.value.find(t => t.id === id)
      if (!template) return
      
      editingId.value = id
      newTemplate.value = {
        template_id: template.template_id,
        name: template.name,
        description: template.description || '',
        field: template.field || 'Custom'
      }
      
      // Would need to fetch the associated test cases from the backend
      selectedTestCases.value = []
      
      showAddForm.value = true
      isEditing.value = true
    }
    
    const deleteTemplate = async (id) => {
      if (confirm('Are you sure you want to delete this template?')) {
        try {
          store.commit('SET_LOADING', true)
          store.commit('SET_ERROR', null)
          
          await axios.delete(`${API_URL}/test-run-templates/${id}`)
          
          // Refresh the list
          await store.dispatch('fetchTestRunTemplates')
          
          alert('Template deleted successfully')
        } catch (error) {
          console.error('Error deleting template:', error)
          store.commit('SET_ERROR', (error.response && error.response.data && error.response.data.detail) || error.message || 'Failed to delete template')
        } finally {
          store.commit('SET_LOADING', false)
        }
      }
    }
    
    const startTestRun = (id) => {
      router.push(`/direct-test-run/${id}`)
    }
    
    return {
      templates,
      testCases,
      testSuites,
      loading,
      error,
      showAddForm,
      isEditing,
      newTemplate,
      searchQuery,
      suiteFilter,
      selectedTestCases,
      filteredTestCases,
      getTemplateTestCaseCount,
      addTemplate,
      editTemplate,
      deleteTemplate,
      startTestRun
    }
  }
}
</script>

<style scoped>
.test-run-templates {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem;
}

.actions {
  margin-bottom: 1rem;
  display: flex;
  justify-content: flex-end;
}

.add-form {
  background-color: #f5f5f5;
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.form-group {
  margin-bottom: 1rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: bold;
}

input[type="text"],
select,
textarea {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ccc;
  border-radius: 4px;
}

textarea {
  resize: vertical;
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  background-color: #e0e0e0;
  margin-right: 0.5rem;
}

.btn.primary {
  background-color: #42b983;
  color: white;
}

.btn.danger {
  background-color: #e53935;
  color: white;
}

.templates-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.template-card {
  background-color: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.template-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #eee;
  padding-bottom: 0.75rem;
}

.template-type {
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.875rem;
  background-color: #f5f5f5;
  color: #666;
}

.template-description {
  color: #666;
  margin: 0;
}

.template-stats {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.test-case-count {
  font-weight: bold;
  color: #42b983;
}

.template-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  margin-top: auto;
}

.test-case-selector {
  border: 1px solid #ccc;
  border-radius: 4px;
  padding: 1rem;
  max-height: 300px;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.filter-controls {
  display: flex;
  gap: 1rem;
}

.filter-controls input,
.filter-controls select {
  flex: 1;
}

.test-case-list {
  overflow-y: auto;
  max-height: 200px;
  border: 1px solid #eee;
  border-radius: 4px;
  padding: 0.5rem;
}

.test-case-item {
  padding: 0.5rem;
  border-bottom: 1px solid #eee;
}

.test-case-item:last-child {
  border-bottom: none;
}

.loading, .error, .empty {
  text-align: center;
  padding: 2rem;
}

.error {
  color: #e53935;
}
</style>
