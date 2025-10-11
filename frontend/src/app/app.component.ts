import { Component } from '@angular/core';
import { Router, NavigationEnd } from '@angular/router';
import { filter } from 'rxjs/operators';

import { MatToolbarModule } from '@angular/material/toolbar';
import { MatIconModule } from '@angular/material/icon';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBarModule } from '@angular/material/snack-bar';
import { RouterOutlet, RouterLink } from '@angular/router';
import { GalleryComponent } from './gallery/gallery.component';
import { HttpClientModule } from '@angular/common/http';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss'],
  standalone: true,
  imports: [MatToolbarModule, MatIconModule, MatFormFieldModule, MatInputModule, MatButtonModule, MatTooltipModule, MatProgressSpinnerModule, MatSnackBarModule, RouterOutlet, RouterLink, HttpClientModule, GalleryComponent, CommonModule]
})
export class AppComponent {
  title = 'Fruitopia';
  public showGalleryArea = true;
  constructor(private router: Router) {
    // hide gallery area on explore routes
    this.router.events.pipe(filter(e => e instanceof NavigationEnd)).subscribe((ev: any) => {
      const url: string = ev.urlAfterRedirects || ev.url || '';
      // hide the embedded gallery area when the app route is the gallery page or explore pages
      this.showGalleryArea = !(url.startsWith('/explore') || url.startsWith('/gallery'));
    });
  }
}
