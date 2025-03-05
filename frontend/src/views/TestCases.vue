<template>
  <div class="test-cases">
    <h1>Test Cases</h1>
    
    <div class="actions">
      <button @click="showAddForm = !showAddForm" class="btn primary">
        {{ showAddForm ? 'Cancel' : 'Add Test Case' }}
      </button>
      <button @click="removeAllTestCases" class="btn danger">
        Remove All Test Cases
      </button>
    </div>
    
    <div v-if="showAddForm" class="add-form">
      <h2>{{ isEditing ? 'Edit Test Case' : 'Add New Test Case' }}</h2>
      <form @submit.prevent="addTestCase">
        <div class="form-group">
          <label for="id">ID:</label>
          <input type="text" id="id" v-model="newTestCase.id" required>
        </div>
        
        <div class="form-group">
          <label for="title">Title:</label>
          <input type="text" id="title" v-model="newTestCase.title" required>
        </div>
        
        <div class="form-group">
          <label for="test_suite_id">Test Suite:</label>
          <select id="test_suite_id" v-model="newTestCase.test_suite_id" required>
            <option v-for="suite in testSuites" :key="suite.id" :value="suite.id">
              {{ suite.name }}
            </option>
          </select>
        </div>
        
        <div class="form-group">
          <label for="version">Version:</label>
          <input type="number" id="version" v-model.number="newTestCase.version" required>
        </div>
        
        <div class="form-group">
          <label for="version_string">Version String:</label>
          <input type="text" id="version_string" v-model="newTestCase.version_string" required>
        </div>
        
        <div class="form-group">
          <label for="description">Description:</label>
          <textarea id="description" v-model="newTestCase.description" rows="3"></textarea>
        </div>
        
        <div class="form-group">
          <label for="steps">Steps:</label>
          <textarea id="steps" v-model="newTestCase.steps" rows="3"></textarea>
        </div>
        
        <div class="form-group">
          <label for="precondition">Precondition:</label>
          <textarea id="precondition" v-model="newTestCase.precondition" rows="2"></textarea>
        </div>
        
        <div class="form-group">
          <label for="area">Area:</label>
          <input type="text" id="area" v-model="newTestCase.area">
        </div>
        
        <div class="form-group">
          <label for="automatability">Automatability:</label>
          <select id="automatability" v-model="newTestCase.automatability">
            <option value="Yes">Yes</option>
            <option value="No">No</option>
            <option value="Manual">Manual</option>
          </select>
        </div>
        
        <div class="form-group">
          <label for="author">Author:</label>
          <input type="text" id="author" v-model="newTestCase.author">
        </div>
        
        <div class="form-group">
          <label for="is_challenged">Is Challenged:</label>
          <input type="checkbox" id="is_challenged" v-model="newTestCase.is_challenged">
        </div>
        
        <button type="submit" class="btn primary">{{ isEditing ? 'Update Test Case' : 'Add Test Case' }}</button>
      </form>
    </div>
    
    <div v-if="loading" class="loading">Loading...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="testCases.length === 0" class="empty">No test cases available</div>
    <div v-else class="test-cases-list">
      <div class="table-container">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Title</th>
              <th>Test Suite</th>
              <th>Version</th>
              <th>Area</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="testCase in testCases" :key="testCase.id">
              <td>{{ testCase.id }}</td>
              <td>{{ testCase.title }}</td>
              <td>{{ testCase.test_suite_id }}</td>
              <td>{{ testCase.version_string }}</td>
              <td>{{ testCase.area || '-' }}</td>
              <td>
                <button @click="viewTestCase(testCase.id)" class="btn small">View</button>
                <button @click="editTestCase(testCase.id)" class="btn small">Edit</button>
                <button @click="deleteTestCase(testCase.id)" class="btn small danger">Delete</button>
              </td>
            </tr>
          </tbody>
        </table>
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
  name: 'TestCases',
  setup() {
    const store = useStore()
    const router = useRouter()
    const showAddForm = ref(false)
    const isEditing = ref(false)
    
    const newTestCase = ref({
      id: '',
      title: '',
      version: 1,
      version_string: '1.0',
      test_suite_id: '',
      applies_to: '',
      description: '',
      steps: '',
      precondition: '',
      area: '',
      automatability: 'Manual',
      author: '',
      material: '',
      is_challenged: false,
      challenge_issue_url: ''
    })
    
    onMounted(() => {
      store.dispatch('fetchTestCases')
      store.dispatch('fetchTestSuites')
    })
    
    // Filter out duplicate test cases by case_id
    const testCases = computed(() => {
      const uniqueCases = new Map();
      store.state.testCases.forEach(testCase => {
        // Use case_id as the unique identifier
        if (testCase.case_id && !uniqueCases.has(testCase.case_id)) {
          uniqueCases.set(testCase.case_id, testCase);
        }
      });
      return Array.from(uniqueCases.values());
    });
    
    const testSuites = computed(() => store.state.testSuites)
    const loading = computed(() => store.state.loading)
    const error = computed(() => store.state.error)
    
    const addTestCase = ref(async () => {
      try {
        store.commit('SET_LOADING', true)
        store.commit('SET_ERROR', null)
        
        await axios.post(`${API_URL}/test-cases`, newTestCase.value)
        
        // Reset form
        newTestCase.value = {
          id: '',
          title: '',
          version: 1,
          version_string: '1.0',
          test_suite_id: '',
          applies_to: '',
          description: '',
          steps: '',
          precondition: '',
          area: '',
          automatability: 'Manual',
          author: '',
          material: '',
          is_challenged: false,
          challenge_issue_url: ''
        }
        
        showAddForm.value = false
        
        // Refresh the list
        await store.dispatch('fetchTestCases')
        
        // Show success message
        alert('Test case created successfully')
      } catch (error) {
        console.error('Error adding test case:', error)
        store.commit('SET_ERROR', (error.response && error.response.data && error.response.data.detail) || error.message || 'Failed to add test case')
      } finally {
        store.commit('SET_LOADING', false)
      }
    })
    
    const viewTestCase = (id) => {
      router.push(`/test-cases/${id}`)
    }
    
    const editTestCase = (id) => {
      // Find the test case to edit
      const testCase = testCases.value.find(tc => tc.id === id)
      if (!testCase) return
      
      // Set up the form with current values
      newTestCase.value = {
        title: testCase.title,
        version: testCase.version,
        version_string: testCase.version_string,
        test_suite_id: testCase.test_suite_id,
        applies_to: testCase.applies_to,
        description: testCase.description,
        steps: testCase.steps,
        precondition: testCase.precondition,
        area: testCase.area,
        automatability: testCase.automatability,
        author: testCase.author,
        material: testCase.material,
        is_challenged: testCase.is_challenged,
        challenge_issue_url: testCase.challenge_issue_url
      }
      
      // Show the form and set editing mode
      showAddForm.value = true
      isEditing.value = true
      
      // Update the addTestCase function to handle both create and update
      addTestCase.value = async () => {
        try {
          store.commit('SET_LOADING', true)
          store.commit('SET_ERROR', null)
          
          await axios.put(`${API_URL}/test-cases/${id}`, newTestCase.value)
          
          // Reset form
          newTestCase.value = {
            title: '',
            version: 1,
            version_string: '1.0',
            test_suite_id: '',
            applies_to: '',
            description: '',
            steps: '',
            precondition: '',
            area: '',
            automatability: '',
            author: '',
            material: '',
            is_challenged: false,
            challenge_issue_url: ''
          }
          
          showAddForm.value = false
          isEditing.value = false
          
          // Refresh the list
          await store.dispatch('fetchTestCases')
          
          // Show success message
          alert('Test case updated successfully')
        } catch (error) {
          console.error('Error updating test case:', error)
          store.commit('SET_ERROR', (error.response && error.response.data && error.response.data.detail) || error.message || 'Failed to update test case')
        } finally {
          store.commit('SET_LOADING', false)
        }
      }
    }
    
    const deleteTestCase = async (id) => {
      if (confirm('Are you sure you want to delete this test case?')) {
        try {
          store.commit('SET_LOADING', true)
          store.commit('SET_ERROR', null)
          
          await axios.delete(`${API_URL}/test-cases/${id}`)
          
          // Refresh the lists
          await store.dispatch('fetchTestCases')
          await store.dispatch('fetchTestCaseResults')
          
          // Show success message
          alert('Test case deleted successfully')
        } catch (error) {
          console.error('Error deleting test case:', error)
          store.commit('SET_ERROR', (error.response && error.response.data && error.response.data.detail) || error.message || 'Failed to delete test case')
        } finally {
          store.commit('SET_LOADING', false)
        }
      }
    }
    
    const removeAllTestCases = async () => {
      if (confirm('Are you sure you want to delete ALL test cases? This action cannot be undone.')) {
        try {
          store.commit('SET_LOADING', true)
          store.commit('SET_ERROR', null)
          
          // Call the backend endpoint to clear all test cases
          await axios.delete(`${API_URL}/test-cases/clear-all/`)
          
          // Refresh the lists
          await store.dispatch('fetchTestCases')
          await store.dispatch('fetchTestCaseResults')
          await store.dispatch('fetchTestSuites')
          
          // Show success message
          alert('All test cases have been removed successfully')
        } catch (error) {
          console.error('Error removing all test cases:', error)
          store.commit('SET_ERROR', (error.response && error.response.data && error.response.data.detail) || error.message || 'Failed to remove all test cases')
        } finally {
          store.commit('SET_LOADING', false)
        }
      }
    }
    
    return {
      testCases,
      testSuites,
      loading,
      error,
      showAddForm,
      isEditing,
      newTestCase,
      addTestCase,
      viewTestCase,
      editTestCase,
      deleteTestCase,
      removeAllTestCases
    }
  }
}
</script>

<style scoped>
.test-cases {
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
input[type="number"],
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

.table-container {
  max-height: 70vh;
  overflow-y: auto;
  border: 1px solid #eee;
  border-radius: 4px;
}

thead {
  position: sticky;
  top: 0;
  background-color: white;
  z-index: 1;
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
