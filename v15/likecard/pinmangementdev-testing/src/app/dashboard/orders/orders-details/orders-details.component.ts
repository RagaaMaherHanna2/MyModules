import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { OrdersService } from 'src/app/services/orders/orders.service';
import { Order } from 'src/models/orders/orders';

@Component({
  selector: 'app-orders-details',
  templateUrl: './orders-details.component.html',
  styleUrls: ['./orders-details.component.scss']
})
export class OrdersDetailsComponent implements OnInit {

  order: Order;
  constructor(private activatedRoute: ActivatedRoute,
    private ordersService: OrdersService,
    private router: Router) { }
  ngOnInit(): void {
    this.activatedRoute.params.subscribe((params) => {
      this.ordersService.getOrderDetails(+params['id']).subscribe((res) => {
        if (res.ok) {
          this.order = res.result.data[0];
        }
      });
    });
  }
  get_serial_status_style(state: any) {
    switch (state) {
      case 'Available': {
        return 'default';
      }
      case 'Redeemed': {
        return 'success';
      }
      case 'Expired': {
        return 'danger';
      }
    }
    return 'default';
  }

  getSerialState(state: string) {
    if (state === 'Redeemed')
      return $localize`Sold`
    else
      return state

  }
}
