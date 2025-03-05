<template>
  <div class="test-suites">
    <h1>Test Suites</h1>
    
    <div class="actions">
      <button @click="showAddForm = !showAddForm" class="btn primary">
        {{ showAddForm ? 'Cancel' : 'Add Test Suite' }}
      </button>
    </div>
    
    <div v-if="showAddForm" class="add-form">
      <h2>Add New Test Suite</h2>
      <form @submit.prevent="addTestSuite">
        <div class="form-group">
          <label for="id">ID:</label>
          <input type="text" id="id" v-model="newTestSuite.id" required>
        </div>
        
        <div class="form-group">
          <label for="name">Name:</label>
          <input type="text" id="name" v-model="newTestSuite.name" required>
        </div>
        
        <div class="form-group">
          <label for="url">URL:</label>
          <input type="text" id="url" v-model="newTestSuite.url">
        </div>
        
        <div class="form-group">
          <label for="format">Format:</label>
          <input type="text" id="format" v-model="newTestSuite.format" required>
        </div>
        
        <div class="form-group">
          <label for="version">Version:</label>
          <input type="number" id="version" v-model.number="newTestSuite.version" required>
        </div>
        
        <div class="form-group">
          <label for="version_string">Version String:</label>
          <input type="text" id="version_string" v-model="newTestSuite.version_string" required>
        </div>
        
        <div class="form-group">
          <label for="is_final">Is Final:</label>
          <input type="checkbox" id="is_final" v-model="newTestSuite.is_final">
        </div>
        
        <button type="submit" class="btn primary">Add Test Suite</button>
      </form>
    </div>
    
    <div v-if="loading" class="loading">Loading...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="testSuites.length === 0" class="empty">No test suites available</div>
    <div v-else class="test-suites-list">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Format</th>
            <th>Version</th>
            <th>Is Final</th>
            <th>Test Cases</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="suite in testSuites" :key="suite.id">
            <td>{{ suite.id }}</td>
            <td>{{ suite.name }}</td>
            <td>{{ suite.format }}</td>
            <td>{{ suite.version_string }}</td>
            <td>{{ suite.is_final ? 'Yes' : 'No' }}</td>
            <td>{{ getTestCasesCount(suite.id) }}</td>
            <td>
              <button @click="viewTestSuite(suite.id)" class="btn small">View</button>
              <button @click="editTestSuite(suite.id)" class="btn small">Edit</button>
              <button @click="deleteTestSuite(suite.id)" class="btn small danger">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>
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
  name: 'TestSuites',
  setup() {
    const store = useStore()
    const router = useRouter()
    const showAddForm = ref(false)
    
    const newTestSuite = ref({
      id: '',
      name: '',
      url: '',
      format: '',
      version: 1,
      version_string: '1.0',
      is_final: false
    })
    
    onMounted(async () => {
      console.log("TestSuites component mounted")
      await store.dispatch('fetchTestSuites')
      await store.dispatch('fetchTestCases')
      
      // If no test suites are found, show a message
      if (store.state.testSuites.length === 0) {
        console.log("No test suites found. Try uploading a test file with test suites.")
        // Try again after a short delay in case the database is still being updated
        setTimeout(async () => {
          await store.dispatch('fetchTestSuites')
          console.log(`Retry found ${store.state.testSuites.length} test suites`)
          
          // If still no test suites, try one more time with a longer delay
          if (store.state.testSuites.length === 0) {
            setTimeout(async () => {
              await store.dispatch('fetchTestSuites')
              console.log(`Final retry found ${store.state.testSuites.length} test suites`)
              
              // If still no test suites, create a default one
              if (store.state.testSuites.length === 0) {
                try {
                  console.log("Creating default test suite from component...")
                  const response = await axios.post(`${API_URL}/test-suites`, {
                    id: "DEFAULT",
                    name: "Default Test Suite",
                    format: "json",
                    version: 1,
                    version_string: "1.0",
                    is_final: false
                  })
                  
                  if (response.data) {
                    store.commit('SET_TEST_SUITES', [response.data])
                    console.log("Created default test suite from component:", response.data)
                  }
                } catch (error) {
                  console.error("Error creating default test suite from component:", error)
                }
              }
            }, 5000)
          }
        }, 2000)
      } else {
        console.log(`Found ${store.state.testSuites.length} test suites`)
      }
    })
    
    const testSuites = computed(() => store.state.testSuites)
    const testCases = computed(() => store.state.testCases)
    const loading = computed(() => store.state.loading)
    const error = computed(() => store.state.error)
    
    const getTestCasesCount = (suiteId) => {
      return testCases.value.filter(tc => tc.test_suite_id === suiteId).length
    }
    
    const addTestSuite = async () => {
      try {
        await axios.post(`${API_URL}/test-suites`, newTestSuite.value)
        // Reset form
        newTestSuite.value = {
          id: '',
          name: '',
          url: '',
          format: '',
          version: 1,
          version_string: '1.0',
          is_final: false
        }
        showAddForm.value = false
        // Refresh the list
        store.dispatch('fetchTestSuites')
      } catch (error) {
        console.error('Error adding test suite:', error)
        store.commit('SET_ERROR', error.message || 'Failed to add test suite')
      }
    }
    
    const viewTestSuite = (id) => {
      router.push(`/test-suites/${id}`)
    }
    
    const editTestSuite = (id) => {
      router.push(`/test-suites/${id}/edit`)
    }
    
    const deleteTestSuite = async (id) => {
      if (confirm('Are you sure you want to delete this test suite?')) {
        try {
          await axios.delete(`${API_URL}/test-suites/${id}`)
          // Refresh the list
          store.dispatch('fetchTestSuites')
        } catch (error) {
          console.error('Error deleting test suite:', error)
          store.commit('SET_ERROR', error.message || 'Failed to delete test suite')
        }
      }
    }
    
    return {
      testSuites,
      testCases,
      loading,
      error,
      showAddForm,
      newTestSuite,
      addTestSuite,
      viewTestSuite,
      editTestSuite,
      deleteTestSuite,
      getTestCasesCount
    }
  }
}
</script>

<style scoped>
.test-suites {
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
input[type="number"] {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ccc;
  border-radius: 4px;
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

.btn.small {
  padding: 0.25rem 0.5rem;
  font-size: 0.875rem;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 0.75rem;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

th {
  background-color: #f5f5f5;
  font-weight: bold;
}

tr:hover {
  background-color: #f5f5f5;
}

.loading, .error, .empty {
  text-align: center;
  padding: 2rem;
}

.error {
  color: #e53935;
}
</style>
