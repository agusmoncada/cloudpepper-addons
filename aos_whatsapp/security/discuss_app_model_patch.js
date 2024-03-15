/* @odoo-module */

import { DiscussApp } from "@mail/core/common/discuss_app_model";
import { Record } from "@mail/core/common/record";

import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";

patch(DiscussApp, {
    new(data) {
        const res = super.new(data);
        res.whatsapp = {
            id: "whatsapp",
            name: _t("Whatsapp"),
            isOpen: false,
            canView: false,
            canAdd: true,
            serverStateKey: "is_discuss_sidebar_category_livechat_open",
            addTitle: _t("Start a message"),
            addHotkey: "w",
        };
        // console.log('=DiscussApp=',res.whatsapp)
        return res;
    },
});

patch(DiscussApp.prototype, {
    setup(env) {
        super.setup(env);
        this.whatsapp = Record.one("DiscussAppCategory");
    },
});
