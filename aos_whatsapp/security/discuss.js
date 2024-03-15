/** @odoo-module **/

import { registerPatch } from '@mail/model/model_core';
import { one } from '@mail/model/model_field';

registerPatch({
    name: 'Discuss',
    recordMethods: {
        /**
         * @override
         */
        onInputQuickSearch(value) {
            if (!this.sidebarQuickSearchValue) {
                this.categoryWhatsapp.open();
            }
            return this._super(value);
        },
    },
    fields: {
        /**
         * Discuss sidebar category for `livechat` channel threads.
         */
        categoryWhatsapp: one('DiscussSidebarCategory', {
            default: {},
            inverse: 'discussAsWhatsapp',
        }),
    },
});
