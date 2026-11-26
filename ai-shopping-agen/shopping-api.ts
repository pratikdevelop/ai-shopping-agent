import { inject, Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface ProductSearchRequest {
  query: string;
  budget_amount: number | null;
  currency: 'INR';
  country: string;
  state: string | null;
  city: string | null;
  condition: string;
  specifications: Record<string, string>;
  preferred_retailers: string[];
  include_local_stores: boolean;
}

export interface SearchStatusResponse {
  search_id: string;
  status: 'queued' | 'running' | 'partial' | 'completed' | 'failed' | 'cancelled';
  mode: string;
  query: string;
  message: string;
  warnings: string[];
  created_at: string;
  completed_at: string | null;
}

export interface SearchDealsResponse {
  search_id: string;
  status: SearchStatusResponse['status'];
  mode: string;
  deals: unknown[];
  warnings: string[];
}

@Injectable({ providedIn: 'root' })
export class ShoppingApi {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = '/api/v1/shopping';

  createSearch(payload: ProductSearchRequest): Observable<SearchStatusResponse> {
    return this.http.post<SearchStatusResponse>(`${this.baseUrl}/search`, payload);
  }

  getDeals(searchId: string): Observable<SearchDealsResponse> {
    return this.http.get<SearchDealsResponse>(
      `${this.baseUrl}/search/${encodeURIComponent(searchId)}/deals`,
    );
  }
}
