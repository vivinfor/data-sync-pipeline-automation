import logging

from django.urls import reverse
from django.views import View

logger = logging.getLogger(__name__)

class SidebarContextMixin(View):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_path = self.request.path.lower()

        sidebar_links = []
        
        other_links = [
            {
                'label': 'KPIs',
                'icon': 'rocket',  
                'url': '#',  
                'subitems': [
                    {'label': 'Performance Overview', 'url': '#'},  
                    {'label': 'Target Reports', 'url': '#'},       
                ],
            },
            {
                'label': 'Reports',
                'icon': 'chart-line',  
                'url': '#',  #
                'subitems': [
                    {
                        'label': 'Performance',
                        'url': reverse('dashboard:performance_dashboard'),
                        'icon': 'redo',  
                    },
                ],
            },
            {
                'label': 'Teams',
                'icon': 'users',  
                'url': '#',  
                'subitems': [
                    {'label': 'Team Members', 'url': '#'},         
                    {'label': 'Roles & Permissions', 'url': '#'}, 
                ],
            },
            
        ]
        
        other_links_sorted = sorted(other_links, key=lambda x: x['label'])
        
        sidebar_links.append({
            'label': 'Home',
            'icon': 'home',  # Font Awesome Icon (fa-home)
            'url': reverse('dashboard:deliveries_dashboard'),
            'subitems': [],
        })
        
        sidebar_links.extend(other_links_sorted)
        
        def set_active(menu_items):
            for item in menu_items:
                if item.get('url', '').lower() == current_path:
                    item['active'] = True
                    return True  
                if 'subitems' in item:
                    if set_active(item['subitems']):  
                        item['active'] = True
                        return True
            return False

        # Marcar o item ativo
        set_active(sidebar_links)

        context['sidebar_links'] = sidebar_links
        return context
