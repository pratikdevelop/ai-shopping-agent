import { DatePipe } from '@angular/common';
import { Component, computed, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { HttpErrorResponse } from '@angular/common/http';
import { ShoppingApi, SearchStatusResponse } from './core/services/shopping-api';

@Component({
  selector: 'app-root',
  imports: [DatePipe, ReactiveFormsModule],
  templateUrl: './app.html',
})
export class App {
  private readonly formBuilder = inject(FormBuilder);
  private readonly shoppingApi = inject(ShoppingApi);

  protected readonly isSubmitting = signal(false);
  protected readonly searchResult = signal<SearchStatusResponse | null>(null);
  protected readonly errorMessage = signal('');
  protected readonly dealsMessage = signal('');
  protected readonly activeSection = signal('search');

  protected readonly searchForm = this.formBuilder.nonNullable.group({
    query: ['', [Validators.required, Validators.minLength(3), Validators.maxLength(1000)]],
    budget: ['', [Validators.pattern(/^\d+(\.\d{1,2})?$/)]],
    city: [''],
    state: [''],
    includeLocalStores: [false],
  });

  protected readonly hasSearchResult = computed(() => this.searchResult() !== null);

  protected submitSearch(): void {
    this.errorMessage.set('');
    this.dealsMessage.set('');
    this.searchResult.set(null);

    if (this.searchForm.invalid) {
      this.searchForm.markAllAsTouched();
      return;
    }

    const value = this.searchForm.getRawValue();
    const includeLocalStores = value.includeLocalStores;

    if (includeLocalStores && !value.city.trim() && !value.state.trim()) {
      this.errorMessage.set('Enter a city or state to include physical stores.');
      return;
    }

    const payload = {
      query: value.query.trim(),
      budget_amount: value.budget ? Number(value.budget) : null,
      currency: 'INR' as const,
      country: 'India',
      state: value.state.trim() || null,
      city: value.city.trim() || null,
      condition: 'new',
      specifications: {},
      preferred_retailers: [
        'Amazon India',
        'Flipkart',
        'Croma',
        'Reliance Digital',
        'Vijay Sales',
      ],
      include_local_stores: includeLocalStores,
    };

    this.isSubmitting.set(true);
    this.shoppingApi.createSearch(payload).subscribe({
      next: (result) => {
        this.searchResult.set(result);
        this.isSubmitting.set(false);
        this.dealsMessage.set(
          result.mode === 'placeholder'
            ? 'The API accepted your request. Live retailer research will be connected in a later step.'
            : 'Your shopping research request was submitted.',
        );
      },
      error: (error: HttpErrorResponse) => {
        this.isSubmitting.set(false);
        this.errorMessage.set(this.getErrorMessage(error));
      },
    });
  }

  protected setActiveSection(section: string): void {
    this.activeSection.set(section);
  }

  private getErrorMessage(error: HttpErrorResponse): string {
    if (error.status === 0) {
      return 'Cannot reach the backend. Start the FastAPI server and try again.';
    }

    const detail = error.error?.detail;
    if (typeof detail === 'string') {
      return detail;
    }
    if (detail?.message) {
      return detail.message;
    }

    return `The search request failed (${error.status}). Please try again.`;
  }
}
