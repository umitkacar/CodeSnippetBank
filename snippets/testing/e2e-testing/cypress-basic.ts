// Cypress E2E Testing
// Comprehensive Cypress test examples

describe('Cypress Basic Tests', () => {
  beforeEach(() => {
    cy.visit('https://example.com');
  });

  it('loads the page', () => {
    cy.title().should('include', 'Example');
  });

  it('clicks a button', () => {
    cy.get('button#submit').click();
    cy.get('.success').should('be.visible');
  });

  it('fills out a form', () => {
    cy.get('input[name="email"]').type('test@example.com');
    cy.get('input[name="password"]').type('password123');
    cy.get('button[type="submit"]').click();
    cy.url().should('include', '/dashboard');
  });

  it('checks checkbox', () => {
    cy.get('input[type="checkbox"]').check();
    cy.get('input[type="checkbox"]').should('be.checked');
  });

  it('selects from dropdown', () => {
    cy.get('select').select('option2');
    cy.get('select').should('have.value', 'option2');
  });
});

describe('Cypress Advanced', () => {
  it('intercepts API calls', () => {
    cy.intercept('GET', '/api/users', {
      statusCode: 200,
      body: [{ id: 1, name: 'John' }],
    }).as('getUsers');

    cy.visit('/users');
    cy.wait('@getUsers');
    cy.contains('John').should('be.visible');
  });

  it('uses custom commands', () => {
    cy.login('user@example.com', 'password');
    cy.url().should('include', '/dashboard');
  });

  it('handles file upload', () => {
    cy.get('input[type="file"]').attachFile('test-file.pdf');
    cy.get('.upload-success').should('be.visible');
  });
});
