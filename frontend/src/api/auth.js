/**
 * LawAid Authentication & Registration API
 */
import { apiFetch, authStorage } from './http';

export async function login(email, password) {
  const data = await apiFetch('/api/auth/token/', {
    method: 'POST',
    body: { email, password },
  });

  if (data.access) {
    authStorage.setToken(data.access);
  }
  if (data.user) {
    authStorage.setUser(data.user);
  }
  return data;
}

export async function registerClient(clientData) {
  return await apiFetch('/api/auth/register/client/', {
    method: 'POST',
    body: clientData,
  });
}

/**
 * Register Lawyer with Encrypted Document Upload (FR-2, NFR-4)
 * @param {FormData} formData multipart containing nid_card and bar_council_certificate
 */
export async function registerLawyer(formData) {
  return await apiFetch('/api/auth/register/lawyer/', {
    method: 'POST',
    body: formData,
  });
}

export async function getCurrentUser() {
  const user = await apiFetch('/api/auth/me/');
  authStorage.setUser(user);
  return user;
}

export function logout() {
  authStorage.clearAll();
  window.dispatchEvent(new CustomEvent('lawaid:auth_changed', { detail: null }));
}
