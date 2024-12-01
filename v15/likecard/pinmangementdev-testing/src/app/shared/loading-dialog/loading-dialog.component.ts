import { Component, OnInit } from '@angular/core';
import { createSelector, Store } from '@ngrx/store';
import { loadingFeature } from 'src/store/loadingSlice';

@Component({
  selector: 'app-loading-dialog',
  templateUrl: './loading-dialog.component.html',
  styleUrls: ['./loading-dialog.component.scss'],
})
export class LoadingDialogComponent implements OnInit {
  constructor(private readonly store: Store) {}
  open$ = this.store.select(
    createSelector(loadingFeature, (state) => state.open)
  );

  ngOnInit(): void {}
}
